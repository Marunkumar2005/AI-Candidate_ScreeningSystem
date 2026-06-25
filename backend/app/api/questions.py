from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.models.models import Question, Session
from app.services.question_service import evaluate_answer_with_ai
from app.services.rag_service import rag_service
from app.services.question_service import generate_questions_with_ai
import uuid

router = APIRouter()


class SubmitAnswerRequest(BaseModel):
    answer: str


class AddQuestionRequest(BaseModel):
    session_id: str


@router.post("/{question_id}/answer")
def submit_answer(
    question_id: str,
    request: SubmitAnswerRequest,
    db: DBSession = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    session = db.query(Session).filter(Session.id == question.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    evaluation = evaluate_answer_with_ai(
        question=question.question_text,
        answer=request.answer,
        role=session.role,
        context=question.context_used or ""
    )

    question.answer = request.answer
    question.answer_score = evaluation.get("score", 0.5)
    question.answer_feedback = evaluation.get("feedback", "")
    db.commit()
    db.refresh(question)

    return {
        "question_id": question_id,
        "answer_recorded": True,
        "evaluation": evaluation
    }


@router.post("/generate-more")
def generate_more_questions(request: AddQuestionRequest, db: DBSession = Depends(get_db)):
    """Generate 2 additional questions based on session progress."""
    session = db.query(Session).filter(Session.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    existing = db.query(Question).filter(Question.session_id == request.session_id).all()
    existing_topics = [q.topic for q in existing if q.topic]
    current_count = len(existing)

    query = rag_service.build_query(
        skills=session.extracted_skills or [],
        technologies=session.extracted_technologies or [],
        role=session.role
    )
    context_chunks = rag_service.retrieve_context(query, session.role)

    new_q_data = generate_questions_with_ai(
        role=session.role,
        skills=session.extracted_skills or [],
        technologies=session.extracted_technologies or [],
        context_chunks=context_chunks,
        count=2,
        previous_topics=existing_topics
    )

    new_questions = []
    for i, q in enumerate(new_q_data):
        question = Question(
            id=str(uuid.uuid4()),
            session_id=session.id,
            question_text=q.get("question", ""),
            context_used=context_chunks[i % len(context_chunks)] if context_chunks else "",
            topic=q.get("topic", "General"),
            difficulty=q.get("difficulty", "medium"),
            order_index=current_count + i
        )
        db.add(question)
        new_questions.append({
            "id": question.id,
            "question_text": question.question_text,
            "topic": question.topic,
            "difficulty": question.difficulty,
            "order_index": question.order_index
        })

    db.commit()
    return {"added": len(new_questions), "questions": new_questions}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional, List
from app.db.database import get_db
from app.models.models import Session, Question, SessionSummary
from app.services.rag_service import rag_service
from app.services.question_service import generate_questions_with_ai, generate_session_summary
import uuid

router = APIRouter()


class CreateSessionRequest(BaseModel):
    role: str
    resume_text: str
    candidate_name: Optional[str] = None
    extracted_skills: Optional[List[str]] = []
    extracted_technologies: Optional[List[str]] = []


class SessionResponse(BaseModel):
    id: str
    role: str
    candidate_name: Optional[str]
    status: str
    extracted_skills: List
    extracted_technologies: List
    question_count: int


@router.post("/create")
def create_session(request: CreateSessionRequest, db: DBSession = Depends(get_db)):
    """Create a new interview session and generate initial questions."""
    
    session = Session(
        id=str(uuid.uuid4()),
        role=request.role,
        candidate_name=request.candidate_name or "Candidate",
        resume_text=request.resume_text,
        extracted_skills=request.extracted_skills or [],
        extracted_technologies=request.extracted_technologies or [],
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Build RAG query and retrieve context
    query = rag_service.build_query(
        skills=request.extracted_skills or [],
        technologies=request.extracted_technologies or [],
        role=request.role
    )
    context_chunks = rag_service.retrieve_context(query, request.role)

    # Generate questions
    questions_data = generate_questions_with_ai(
        role=request.role,
        skills=request.extracted_skills or [],
        technologies=request.extracted_technologies or [],
        context_chunks=context_chunks,
        count=6
    )

    for i, q in enumerate(questions_data):
        question = Question(
            id=str(uuid.uuid4()),
            session_id=session.id,
            question_text=q.get("question", ""),
            context_used=context_chunks[i % len(context_chunks)] if context_chunks else "",
            topic=q.get("topic", "General"),
            difficulty=q.get("difficulty", "medium"),
            order_index=i
        )
        db.add(question)
    
    db.commit()

    return {
        "session_id": session.id,
        "candidate_name": session.candidate_name,
        "role": session.role,
        "status": session.status,
        "question_count": len(questions_data)
    }


@router.get("/{session_id}")
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    questions = db.query(Question).filter(
        Question.session_id == session_id
    ).order_by(Question.order_index).all()

    return {
        "id": session.id,
        "role": session.role,
        "candidate_name": session.candidate_name,
        "status": session.status,
        "extracted_skills": session.extracted_skills,
        "extracted_technologies": session.extracted_technologies,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "order_index": q.order_index,
                "answer": q.answer,
                "answer_score": q.answer_score,
                "answer_feedback": q.answer_feedback,
            }
            for q in questions
        ]
    }


@router.post("/{session_id}/complete")
def complete_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "completed"
    questions = db.query(Question).filter(Question.session_id == session_id).all()

    session_data = {
        "role": session.role,
        "questions": [
            {
                "question_text": q.question_text,
                "answer": q.answer,
                "answer_score": q.answer_score
            }
            for q in questions
        ]
    }

    summary_data = generate_session_summary(session_data)

    existing = db.query(SessionSummary).filter(SessionSummary.session_id == session_id).first()
    if existing:
        existing.overall_score = summary_data.get("overall_score")
        existing.strengths = summary_data.get("strengths", [])
        existing.improvements = summary_data.get("improvements", [])
        existing.recommendation = summary_data.get("recommendation")
        existing.summary_text = summary_data.get("summary_text")
    else:
        summary = SessionSummary(
            id=str(uuid.uuid4()),
            session_id=session_id,
            overall_score=summary_data.get("overall_score"),
            strengths=summary_data.get("strengths", []),
            improvements=summary_data.get("improvements", []),
            recommendation=summary_data.get("recommendation"),
            summary_text=summary_data.get("summary_text")
        )
        db.add(summary)

    db.commit()
    return {"status": "completed", "summary": summary_data}


@router.get("/{session_id}/summary")
def get_summary(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    summary = db.query(SessionSummary).filter(SessionSummary.session_id == session_id).first()
    questions = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()

    return {
        "session": {
            "id": session.id,
            "role": session.role,
            "candidate_name": session.candidate_name,
            "status": session.status,
            "skills": session.extracted_skills,
            "technologies": session.extracted_technologies,
        },
        "summary": {
            "overall_score": summary.overall_score if summary else None,
            "strengths": summary.strengths if summary else [],
            "improvements": summary.improvements if summary else [],
            "recommendation": summary.recommendation if summary else None,
            "summary_text": summary.summary_text if summary else None,
        },
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "answer": q.answer,
                "answer_score": q.answer_score,
                "answer_feedback": q.answer_feedback,
            }
            for q in questions
        ]
    }

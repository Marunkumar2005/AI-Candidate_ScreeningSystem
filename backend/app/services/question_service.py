import openai
import json
import random
from typing import List, Dict
from app.core.config import settings
from app.services.rag_service import rag_service


# Fallback question templates when OpenAI is not available
FALLBACK_QUESTIONS = {
    "AI/ML Engineer": [
        {"question": "Can you explain the bias-variance tradeoff and how you manage it in practice?", "topic": "ML Fundamentals", "difficulty": "medium"},
        {"question": "How does backpropagation work in neural networks? Walk me through the math.", "topic": "Deep Learning", "difficulty": "hard"},
        {"question": "What is overfitting, and what techniques do you use to prevent it?", "topic": "Model Training", "difficulty": "easy"},
        {"question": "Explain how RAG (Retrieval-Augmented Generation) differs from fine-tuning an LLM.", "topic": "LLMs", "difficulty": "hard"},
        {"question": "Compare L1 and L2 regularization. When would you prefer one over the other?", "topic": "Regularization", "difficulty": "medium"},
        {"question": "How would you handle a highly imbalanced dataset for a classification problem?", "topic": "Data Handling", "difficulty": "medium"},
        {"question": "What is the transformer architecture and how does self-attention work?", "topic": "Transformers", "difficulty": "hard"},
        {"question": "Describe the steps you'd take to deploy an ML model to production.", "topic": "MLOps", "difficulty": "medium"},
    ],
    "Backend Engineer": [
        {"question": "How do you design a RESTful API for a social media platform? Walk through your approach.", "topic": "API Design", "difficulty": "medium"},
        {"question": "Explain the difference between SQL and NoSQL databases. When would you choose each?", "topic": "Databases", "difficulty": "easy"},
        {"question": "How does JWT authentication work, and what are its security considerations?", "topic": "Security", "difficulty": "medium"},
        {"question": "What is the CAP theorem and how does it influence distributed system design?", "topic": "Distributed Systems", "difficulty": "hard"},
        {"question": "Describe your approach to database indexing and query optimization.", "topic": "Performance", "difficulty": "medium"},
        {"question": "How would you implement rate limiting in a high-traffic API?", "topic": "Scalability", "difficulty": "medium"},
        {"question": "Explain microservices vs monolithic architecture tradeoffs.", "topic": "Architecture", "difficulty": "medium"},
        {"question": "How do you handle database migrations in a production environment?", "topic": "DevOps", "difficulty": "medium"},
    ],
    "Data Scientist": [
        {"question": "Walk me through your approach to exploratory data analysis on a new dataset.", "topic": "EDA", "difficulty": "easy"},
        {"question": "How do you handle missing data? What strategies do you use?", "topic": "Data Cleaning", "difficulty": "easy"},
        {"question": "Explain the difference between precision and recall. When is each more important?", "topic": "Evaluation Metrics", "difficulty": "medium"},
        {"question": "How would you design an A/B test for a new recommendation algorithm?", "topic": "Statistics", "difficulty": "hard"},
        {"question": "Describe feature selection techniques and when you'd use each.", "topic": "Feature Engineering", "difficulty": "medium"},
        {"question": "What is gradient boosting and how does it differ from random forests?", "topic": "Ensemble Methods", "difficulty": "hard"},
        {"question": "How do you communicate complex findings to non-technical stakeholders?", "topic": "Communication", "difficulty": "medium"},
        {"question": "Describe a challenging data pipeline you've built or worked with.", "topic": "Data Engineering", "difficulty": "medium"},
    ],
    "Full Stack Engineer": [
        {"question": "How do you manage state in a large React application?", "topic": "Frontend", "difficulty": "medium"},
        {"question": "Explain the differences between server-side rendering and client-side rendering.", "topic": "Web Architecture", "difficulty": "medium"},
        {"question": "How would you optimize a slow database query in a full-stack application?", "topic": "Performance", "difficulty": "hard"},
        {"question": "Describe how you'd implement real-time features like notifications.", "topic": "Real-time", "difficulty": "medium"},
        {"question": "How do you handle authentication across frontend and backend?", "topic": "Security", "difficulty": "medium"},
        {"question": "Explain your approach to CI/CD pipelines for a full-stack app.", "topic": "DevOps", "difficulty": "medium"},
        {"question": "What are Web Vitals and how do you improve them?", "topic": "Performance", "difficulty": "easy"},
        {"question": "How do you design a RESTful vs GraphQL API and when to choose each?", "topic": "API Design", "difficulty": "medium"},
    ],
    "Frontend Engineer": [
        {"question": "Explain the React reconciliation algorithm and the virtual DOM.", "topic": "React Internals", "difficulty": "hard"},
        {"question": "How do you approach CSS architecture for large-scale applications?", "topic": "CSS", "difficulty": "medium"},
        {"question": "What are Core Web Vitals and how do you optimize for them?", "topic": "Performance", "difficulty": "medium"},
        {"question": "How do you ensure accessibility in your frontend applications?", "topic": "Accessibility", "difficulty": "medium"},
        {"question": "Explain how closures work in JavaScript and give a practical example.", "topic": "JavaScript", "difficulty": "medium"},
        {"question": "How do you handle complex async operations in JavaScript?", "topic": "Async", "difficulty": "medium"},
        {"question": "What is TypeScript and what benefits does it bring over JavaScript?", "topic": "TypeScript", "difficulty": "easy"},
        {"question": "Describe your approach to responsive design and mobile-first development.", "topic": "Responsive Design", "difficulty": "easy"},
    ]
}


def generate_questions_with_ai(
    role: str,
    skills: List[str],
    technologies: List[str],
    context_chunks: List[str],
    count: int = 5,
    previous_topics: List[str] = None
) -> List[Dict]:
    """Generate interview questions using OpenAI with RAG context."""
    
    if not settings.OPENAI_API_KEY:
        return _get_fallback_questions(role, count, previous_topics)

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    context = "\n\n".join(context_chunks[:4])
    skills_str = ", ".join(skills[:8]) if skills else "general"
    tech_str = ", ".join(technologies[:8]) if technologies else "general"
    avoid = f"Avoid questions on these already-covered topics: {', '.join(previous_topics)}." if previous_topics else ""

    prompt = f"""You are an expert technical interviewer for {role} positions.

Candidate Profile:
- Skills: {skills_str}
- Technologies: {tech_str}

Relevant Knowledge Base Context:
{context}

{avoid}

Generate exactly {count} interview questions. Mix difficulty levels (easy/medium/hard).
Each question should test conceptual understanding and practical application.
Tailor questions to match the candidate's background.

Return ONLY a JSON array like:
[
  {{
    "question": "Full question text",
    "topic": "Topic area",
    "difficulty": "easy|medium|hard",
    "context_hint": "brief note on what knowledge this tests"
  }}
]

No markdown, no explanation, just the JSON array."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(text)
        return questions[:count]
    except Exception as e:
        print(f"Question generation error: {e}")
        return _get_fallback_questions(role, count, previous_topics)


def evaluate_answer_with_ai(
    question: str,
    answer: str,
    role: str,
    context: str = ""
) -> Dict:
    """Evaluate a candidate's answer using OpenAI."""
    
    if not settings.OPENAI_API_KEY or not answer.strip():
        return {
            "score": 0.5,
            "feedback": "Answer recorded. AI evaluation requires OpenAI API key.",
            "strengths": [],
            "improvements": ["Configure OpenAI API key for detailed feedback"]
        }

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""You are evaluating a technical interview answer for a {role} position.

Question: {question}
Candidate Answer: {answer}
{f"Reference Context: {context[:500]}" if context else ""}

Evaluate the answer and return ONLY valid JSON:
{{
  "score": 0.0-1.0,
  "feedback": "2-3 sentence overall assessment",
  "strengths": ["strength1", "strength2"],
  "improvements": ["area1", "area2"]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return {
            "score": 0.5,
            "feedback": "Answer recorded successfully.",
            "strengths": ["Response provided"],
            "improvements": []
        }


def generate_session_summary(session_data: Dict) -> Dict:
    """Generate a final session summary."""
    questions = session_data.get("questions", [])
    answered = [q for q in questions if q.get("answer")]
    
    if not settings.OPENAI_API_KEY or not answered:
        avg_score = sum(q.get("answer_score", 0.5) for q in answered) / len(answered) if answered else 0
        return {
            "overall_score": round(avg_score, 2),
            "strengths": ["Technical knowledge demonstrated", "Completed interview session"],
            "improvements": ["Configure OpenAI API key for detailed analysis"],
            "recommendation": "Review Required",
            "summary_text": f"Candidate completed {len(answered)}/{len(questions)} questions."
        }

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    qa_summary = "\n".join([
        f"Q: {q['question_text']}\nA: {q.get('answer', 'No answer')[:200]}\nScore: {q.get('answer_score', 'N/A')}"
        for q in answered[:6]
    ])

    prompt = f"""Summarize this technical interview for a {session_data['role']} position.

Interview Q&A:
{qa_summary}

Return ONLY valid JSON:
{{
  "overall_score": 0.0-1.0,
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["area1", "area2"],
  "recommendation": "Strong Hire|Hire|Maybe|No Hire",
  "summary_text": "3-4 sentence overall assessment"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        avg = sum(q.get("answer_score", 0.5) for q in answered) / len(answered) if answered else 0
        return {
            "overall_score": round(avg, 2),
            "strengths": ["Completed interview"],
            "improvements": [],
            "recommendation": "Review Required",
            "summary_text": f"Completed {len(answered)} questions."
        }


def _get_fallback_questions(role: str, count: int, previous_topics: List[str] = None) -> List[Dict]:
    pool = FALLBACK_QUESTIONS.get(role, FALLBACK_QUESTIONS["AI/ML Engineer"])
    if previous_topics:
        pool = [q for q in pool if q["topic"] not in previous_topics] or pool
    selected = random.sample(pool, min(count, len(pool)))
    return [{"question": q["question"], "topic": q["topic"], "difficulty": q["difficulty"], "context_hint": ""} for q in selected]

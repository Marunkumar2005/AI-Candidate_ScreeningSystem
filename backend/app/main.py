from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import sessions, resume, questions, health
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview System",
    description="RAG-powered candidate screening system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

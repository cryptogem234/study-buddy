from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import questions, sessions, achievements, progress, mastery

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Buddy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(achievements.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(mastery.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Study Buddy API is running"}

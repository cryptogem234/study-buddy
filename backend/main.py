from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
import models  # noqa: F401 — registers all models with Base
from routers import subjects, topics, lessons, questions, progress, vocabulary

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Buddy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(subjects.router)
app.include_router(topics.router)
app.include_router(lessons.router)
app.include_router(questions.router)
app.include_router(progress.router)
app.include_router(vocabulary.router)

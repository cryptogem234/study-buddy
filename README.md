# Study Buddy

Grade 7 learning app — React + FastAPI + SQLite.

## Quick Start

### Backend

## cd backend
## uvicorn main:app --reload

## cd frontend
## npm run dev



```bash
cd backend
pip install -r requirements.txt
python seed_data.py        # populate DB with questions + achievements
uvicorn main:app --reload  # runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                # runs on http://localhost:5173
```

## Project Structure

```
study-buddy/
  backend/
    main.py              # FastAPI app, CORS, router mounts
    database.py          # SQLAlchemy engine + get_db dependency
    models.py            # Question, QuizSession, Answer, Achievement
    routers/
      questions.py       # GET /api/questions, POST /api/questions/check
      sessions.py        # POST/PUT/GET /api/sessions
      achievements.py    # GET/POST /api/achievements
      progress.py        # GET /api/progress/*
    seed_data.py         # 20 questions + 3 achievements
    requirements.txt
  frontend/
    src/
      api.js             # Thin fetch wrapper
      App.jsx            # Router setup
      components/        # Layout, QuizCard, ScoreBoard, AchievementBadge, ProgressChart
      pages/             # Home, Quiz, Progress, Achievements
```

## Subjects

- **English** — Grammar, parts of speech, punctuation, vocabulary (10 questions)
- **Science** — Cells, photosynthesis, ecosystems, water cycle, forces (10 questions)

## Achievements

| Slug | Name | Condition |
|------|------|-----------|
| first-quiz | First Quiz | Complete 1 session |
| perfect-score | Perfect Score | 100% on a session |
| on-a-roll | On a Roll | Complete 5 sessions |

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/questions | List questions (subject, topic, limit filters) |
| POST | /api/questions/check | Check an answer |
| POST | /api/sessions | Start a session |
| PUT | /api/sessions/{id}/complete | Complete a session |
| GET | /api/sessions | Session history |
| GET | /api/achievements | All achievements |
| POST | /api/achievements/check | Award new achievements |
| GET | /api/progress/summary | Overall stats |
| GET | /api/progress/by-subject | Per-subject breakdown |
| GET | /api/progress/chart | Daily scores (last 30 days) |

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./study_buddy.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Columns added after the first release. create_all() only creates missing
# tables, so existing databases (including the laptop copy) get these via ALTER.
ADDED_COLUMNS = {
    "subjects": {"archived": "integer default 0", "position": "integer default 0"},
    "topics": {"hidden": "integer default 0"},
    "lessons": {"extras": "json"},
    "questions": {"skill": "varchar(50) default ''", "difficulty": "varchar(20) default ''"},
    "quiz_attempts": {"level": "varchar(20) default 'core'", "answers": "json"},
    "vocabulary_words": {"level": "varchar(20) default ''"},
}


def ensure_schema():
    Base.metadata.create_all(bind=engine)
    existing_tables = inspect(engine).get_table_names()
    with engine.begin() as conn:
        for table, columns in ADDED_COLUMNS.items():
            if table not in existing_tables:
                continue
            have = {c["name"] for c in inspect(conn).get_columns(table)}
            for name, ddl in columns.items():
                if name not in have:
                    conn.execute(text(f"alter table {table} add column {name} {ddl}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

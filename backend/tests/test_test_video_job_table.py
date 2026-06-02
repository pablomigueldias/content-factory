from sqlalchemy import inspect

from app.core.db import engine


def test_video_job_table_exists():
    inspector = inspect(engine)
    assert "video_jobs" in inspector.get_table_names()


def test_video_job_table_columns():
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("video_jobs")}
    expected = {"id", "topic", "status", "error", "created_at", "updated_at"}
    assert expected.issubset(columns)

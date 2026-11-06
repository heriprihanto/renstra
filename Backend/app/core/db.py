from typing import Generator
from sqlmodel import Session, create_engine
from app.core.config import settings

# create_engine using standard psycopg2 driver
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

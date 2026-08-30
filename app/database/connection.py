from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
#tao engine cau noi giua ung dung va database
engine = create_engine(
    settings.database_url,
    #kiem tra ket noi truoc khi dung tranh loi “MySQL server has gone away”
    pool_pre_ping=True,
    #tai su dung connection sau 280 giay de tranh timeout
    pool_recycle=280,
    echo=settings.debug,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
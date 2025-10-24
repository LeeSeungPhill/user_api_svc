from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL 연결 정보
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:asdf1234@192.168.50.81:5432/fund_risk_mng"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

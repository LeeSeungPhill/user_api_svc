from dotenv import load_dotenv
import os, secrets

load_dotenv()  # .env에서 불러오게 하려면 프로젝트 루트에 .env 파일 추가

SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(64)
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 15)  # 짧은 만료(예: 15분)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or 14)    # 리프레시 토큰 유효일
LOCKOUT_THRESHOLD = int(os.getenv("LOCKOUT_THRESHOLD") or 5)  # 실패 시도 횟수 제한
LOCKOUT_MINUTES = int(os.getenv("LOCKOUT_MINUTES") or 15)      # 잠금 시간(분)
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+psycopg2://postgres:asdf1234@localhost:5432/fund_risk_mng"

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import config, database, crud, models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # token URL not used directly in our login route but required by FastAPI

def hash_password(pw: str):
    return pwd_context.hash(pw)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, expires_delta: timedelta | None = None):
    now = datetime.now(timezone.utc)
    exp = now + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(subject), "iat": now.timestamp(), "exp": exp.timestamp()}
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

def create_refresh_token(subject: str, expires_delta: timedelta | None = None):
    now = datetime.now(timezone.utc)
    exp = now + (expires_delta or timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS))
    payload = {"sub": str(subject), "iat": now.timestamp(), "exp": exp.timestamp(), "type": "refresh"}
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except JWTError:
        return None

# 로그인 시도 처리 (checks lockout, password verify, logging, lock logic)
def attempt_login(db: Session, acct_no: int, password: str, ip: str | None = None):
    acc = crud.get_account(db, acct_no)
    if not acc:
        # 로그 남기기 (acct_no 없음)
        crud.log_login_attempt(db, None, ip, False, "account_not_found")
        return None, "account_not_found"

    # 계정 잠금 확인
    if acc.locked_until:
        now = datetime.now(timezone.utc)
        if acc.locked_until > now:
            crud.log_login_attempt(db, acct_no, ip, False, "account_locked")
            return None, "account_locked"

    # 비밀번호 검사
    if not acc.login_pw or not verify_password(password, acc.login_pw):
        # 실패 로깅 및 카운트 증가
        crud.increment_failed_attempt(db, acct_no)
        crud.log_login_attempt(db, acct_no, ip, False, "invalid_password")
        # lockout 체크
        if acc.failed_attempts + 1 >= config.LOCKOUT_THRESHOLD:
            until = datetime.now(timezone.utc) + timedelta(minutes=config.LOCKOUT_MINUTES)
            crud.lock_account_until(db, acct_no, until)
        return None, "invalid_password"

    # 성공
    crud.reset_failed_attempts(db, acct_no)
    crud.log_login_attempt(db, acct_no, ip, True, "login_success")
    # 발급할 토큰
    access = create_access_token(subject=str(acct_no))
    refresh = create_refresh_token(subject=str(acct_no))
    # DB에 저장
    crud.set_login_tokens(db, acct_no, access, refresh)
    return {"access_token": access, "refresh_token": refresh}, None

# 의존성: 보호된 endpoint에서 현재 사용자 가져오기
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.SessionLocal)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    acct_no = int(sub)
    acc = crud.get_account(db, acct_no)
    if not acc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    # 선택적 검증: 발급된 access token과 비교하여 토큰 탈취 방지 (권장)
    if not acc.login_access_token or acc.login_access_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked or mismatched")
    # 계정 잠금 확인
    if acc.locked_until:
        now = datetime.now(timezone.utc)
        if acc.locked_until > now:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account locked")
    return acc

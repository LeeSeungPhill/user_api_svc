from sqlalchemy.orm import Session
from datetime import datetime, timezone
from . import models, schemas, auth

def create_user(db: Session, user: schemas.StockAccountCreate):
    hashed_pw = auth.hash_password(user.login_pass)
    db_user = models.StockAccount(
        acct_no=user.acct_no,
        nick_name=user.nick_name,
        tel_no=user.tel_no,
        access_token="",
        token_publ_date="",
        app_key="",
        app_secret="",
        last_chg_date=datetime.now(timezone.utc),
        login_pass=hashed_pw,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, acct_no: int, password: str):
    user = db.query(models.StockAccount).filter(models.StockAccount.acct_no == acct_no).first()
    if not user or not auth.verify_password(password, user.login_pass):
        return None
    return user

def get_user_by_acct_no(db: Session, acct_no: int):
    return db.query(models.StockAccount).filter(models.StockAccount.acct_no == acct_no).first()

def update_login_access_token(db: Session, acct_no: int, token: str):
    """로그인 성공 시 login_access_token 컬럼 업데이트"""
    user = db.query(models.StockAccount).filter(models.StockAccount.acct_no == acct_no).first()
    if user:
        user.login_access_token = token
        user.last_chg_date = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    return None

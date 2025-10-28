from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone
from typing import Optional

def get_account(db: Session, acct_no: int):
    return db.query(models.StockAccount).filter(models.StockAccount.acct_no == acct_no).first()

def create_account(db: Session, acct_no: int, nick_name: str, tel_no: str, hashed_pw: str, app_key: str, app_secret: str, bot_token1: str, bot_token2: str):
    acc = models.StockAccount(
        acct_no=acct_no,
        nick_name=nick_name,
        access_token="",
        token_publ_date="",
        tel_no=tel_no,
        app_key=app_key,
        app_secret=app_secret,
        bot_token1=bot_token1,
        bot_token2=bot_token2,
        last_chg_date=datetime.now(timezone.utc),
        login_pw=hashed_pw,
        failed_attempts=0,
        locked_until=None
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc

def increment_failed_attempt(db: Session, acct_no: int):
    acc = get_account(db, acct_no)
    if not acc:
        return None
    acc.failed_attempts = (acc.failed_attempts or 0) + 1
    db.commit()
    db.refresh(acc)
    return acc

def reset_failed_attempts(db: Session, acct_no: int):
    acc = get_account(db, acct_no)
    if not acc:
        return None
    acc.failed_attempts = 0
    acc.locked_until = None
    db.commit()
    db.refresh(acc)
    return acc

def lock_account_until(db: Session, acct_no: int, until_dt):
    acc = get_account(db, acct_no)
    if not acc:
        return None
    acc.locked_until = until_dt
    db.commit()
    db.refresh(acc)
    return acc

def log_login_attempt(db: Session, acct_no: Optional[int], ip: Optional[str], success: bool, reason: Optional[str]=None):
    entry = models.LoginAttempt(acct_no=acct_no, ip=ip, success=success, reason=reason)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def update_profile(db: Session, acct_no: int, nick_name: Optional[str]=None, tel_no: Optional[str]=None, hashed_pw: Optional[str]=None, app_key: Optional[str]=None, app_secret: Optional[str]=None, bot_token1: Optional[str]=None, bot_token2: Optional[str]=None):
    acc = get_account(db, acct_no)
    if not acc:
        return None
    if nick_name is not None:
        acc.nick_name = nick_name
    if tel_no is not None:
        acc.tel_no = tel_no
    if hashed_pw is not None:
        acc.login_pw = hashed_pw
    if app_key is not None:
        acc.app_key = app_key
    if app_secret is not None:
        acc.app_secret = app_secret
    if bot_token1 is not None:
        acc.bot_token1 = bot_token1
    if bot_token2 is not None:
        acc.bot_token2 = bot_token2
    acc.last_chg_date = datetime.now(timezone.utc)
    db.commit()
    db.refresh(acc)
    return acc

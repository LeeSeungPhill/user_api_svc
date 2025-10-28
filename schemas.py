from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    acct_no: int
    nick_name: str
    tel_no: str
    login_pw: str
    app_key: str
    app_secret: str
    bot_token1: str
    bot_token2: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class ProfileOut(BaseModel):
    acct_no: int
    nick_name: str
    tel_no: str
    app_key: str
    app_secret: str
    bot_token1: str
    bot_token2: str
    last_chg_date: datetime

    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    nick_name: Optional[str]
    tel_no: Optional[str]
    change_pw: Optional[str]  # 새 비밀번호(선택)
    app_key: Optional[str]
    app_secret: Optional[str]
    bot_token1: Optional[str]
    bot_token2: Optional[str]

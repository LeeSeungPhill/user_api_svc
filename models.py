from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class StockAccount(Base):
    __tablename__ = "stockAccount_stock_account"

    acct_no = Column(Integer, primary_key=True, index=True)
    nick_name = Column(String(100), nullable=False)
    access_token = Column(String(400), nullable=False)
    token_publ_date = Column(String(14), nullable=False)
    app_key = Column(String(100), nullable=False)
    app_secret = Column(String(200), nullable=False)
    tel_no = Column(String(11), nullable=False)
    last_chg_date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    bot_token1 = Column(String(400))
    bot_token2 = Column(String(400))
    login_access_token = Column(String(400))
    login_pass = Column(String(200))

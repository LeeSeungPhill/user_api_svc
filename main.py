from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import database, models, schemas, crud, auth
from datetime import timedelta

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Stock Account Login API")

# DB 세션 의존성
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 회원가입
@app.post("/register", response_model=schemas.StockAccountResponse)
def register(user: schemas.StockAccountCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    return db_user

# 로그인 (JWT 발급)
@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, int(form_data.username), form_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=60)
    access_token = auth.create_access_token(
        data={"sub": str(user.acct_no)}, expires_delta=access_token_expires
    )

    # 🔹 DB에 로그인 토큰 저장
    crud.update_login_access_token(db, user.acct_no, access_token)

    return {"login_access_token": access_token, "token_type": "bearer"}

# 인증 테스트용 API
@app.get("/me")
def read_users_me(current_user: models.StockAccount = Depends(auth.get_current_user)):
    return {"acct_no": current_user.acct_no, "nick_name": current_user.nick_name}

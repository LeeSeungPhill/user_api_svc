# user_api_svc/routers.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from . import crud, schemas, auth, database, models
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

# register
@router.post("/register", response_model=schemas.ProfileOut)
def register(req: schemas.RegisterRequest, db: Session = Depends(database.get_db)):
    # 이미 존재하면 에러
    existing = crud.get_account(db, req.acct_no)
    if existing:
        raise HTTPException(status_code=400, detail="acct_no already exists")
    hashed = auth.hash_password(req.login_pw)
    acc = crud.create_account(db, req.acct_no, req.nick_name, req.tel_no, hashed, req.app_key, req.app_secret, req.bot_token1, req.bot_token2)
    return acc

# login -> returns access+refresh (uses form data: username=acct_no, password=login_pw)
@router.post("/login", response_model=schemas.TokenResponse)
def login_for_tokens(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: Session = Depends(database.get_db)):
    client_ip = request.client.host if request else None
    try:
        acct_no = int(form_data.username)
    except ValueError:
        raise HTTPException(status_code=400, detail="acct_no must be integer")
    tokens, reason = auth.attempt_login(db, acct_no, form_data.password, client_ip)
    if reason:
        if reason == "account_locked":
            raise HTTPException(status_code=403, detail="Account locked. Try later.")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"], "token_type": "bearer"}

# refresh token -> issue new pair
@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(req: schemas.RefreshRequest, db: Session = Depends(database.get_db)):
    payload = auth.decode_token(req.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    # check type if set
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")
    acct_no = int(payload.get("sub"))
    
    # issue new tokens
    new_access = auth.create_access_token(subject=str(acct_no))
    new_refresh = auth.create_refresh_token(subject=str(acct_no))
    
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

# get my profile (protected)
@router.get("/me")
def read_users_me(request: Request, db: Session = Depends(database.get_db), token: str = Depends(auth.oauth2_scheme)):
    payload = auth.decode_token(token)
    print("디코딩된 payload 1 : ", payload)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    acct_no = int(sub)
    acc = crud.get_account(db, acct_no)
    if not acc:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "acct_no": acc.acct_no,
        "nick_name": acc.nick_name,
        "tel_no": acc.tel_no,
        "app_key": acc.app_key,
        "app_secret": acc.app_secret,
        "bot_token1": acc.bot_token1,
        "bot_token2": acc.bot_token2,
        "token_publ_date": acc.token_publ_date,
    }
 
# update my profile (protected)
@router.put("/me", response_model=schemas.ProfileOut)
def update_my_profile(payload_update: schemas.ProfileUpdate, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(database.get_db)):
    payload = auth.decode_token(token)
    print("디코딩된 payload 3 : ", payload)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    acct_no = int(sub)

    hashed = None
    if payload_update.change_pw:
        hashed = auth.hash_password(payload_update.change_pw)
    acc = crud.update_profile(db, acct_no, payload_update.nick_name, payload_update.tel_no, hashed, payload_update.app_key, payload_update.app_secret, payload_update.bot_token1, payload_update.bot_token2)
    if not acc:
        raise HTTPException(status_code=404, detail="Not found")
    return acc

# admin / list users (protected - could restrict further)
@router.get("/userlist")
def list_users(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(database.get_db)):
    payload = auth.decode_token(token)
    print("디코딩된 payload 2 :", payload)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return db.query(models.StockAccount).all()

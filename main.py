from fastapi import FastAPI
from user_api_svc.database import engine, Base
from user_api_svc import models
from fastapi.middleware.cors import CORSMiddleware
from user_api_svc.routers import router as api_router

# create tables if not exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockAccount Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.50.40:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

from fastapi import FastAPI
from .database import engine, Base
from . import models
from .routers import router as api_router

# create tables if not exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockAccount Auth API")

app.include_router(api_router)

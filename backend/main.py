from fastapi import FastAPI

from database import engine, Base
import models

# Create FastAPI app
app = FastAPI(
    title="Zomato Notes API",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Welcome to Zomato Notes API"
    }
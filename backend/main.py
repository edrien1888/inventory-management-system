from fastapi import FastAPI
from sqlalchemy import text

import models
from database import Base, engine


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
                return {
                "message": "Backend funcionando correctamente"
    }


@app.get("/test-db")
def test_database():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "message": "PostgreSQL conectado correctamente"
    }
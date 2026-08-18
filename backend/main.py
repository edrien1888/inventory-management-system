from fastapi import FastAPI
from sqlalchemy import  text

from database import engine

app = FastAPI()

@app.get("/")
def home():
                return{
                                "mensage":"Backend funcionando correctamente"
                }

@app.get("/test-db")
def home():
                with engine.connect() as connection:
                                connection.execute(text("SELECT 1"))
                                
                return{
                                "message":"PostgreSQL conectado correctamente"
                }
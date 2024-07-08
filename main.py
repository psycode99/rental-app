from fastapi import FastAPI
from database import engine
import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def main():
    return{"message": "rental api"}
from fastapi import FastAPI
from database import engine
import models
from routers import users


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def main():
    return{"message": "rental api"}


app.include_router(users.router)
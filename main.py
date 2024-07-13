from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine
import models
from routers import users, property, auth, uploads, bookings, maintenance_requests


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount('/static', StaticFiles(directory="static"), name="static")

@app.get('/')
def main():
    return{"message": "rental api"}


app.include_router(users.router)
app.include_router(property.router)
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(bookings.router)
app.include_router(maintenance_requests.router)
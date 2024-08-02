from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine
from . import models
from pathlib import Path
from .routers import users, property, auth, uploads, bookings, maintenance_requests, tenant_applications, payments

models.Base.metadata.create_all(bind=engine)

current_file = Path(__file__)
current_file_dir = current_file.parent
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
static_root_absolute = project_root_absolute /"app"/"static"
print(static_root_absolute)

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
app.include_router(tenant_applications.router)
app.include_router(payments.router)
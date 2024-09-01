from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine, SessionLocal
from . import models, utils
from pathlib import Path
import threading
import time
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from . import config
from .routers import users, property, auth, uploads, bookings, maintenance_requests, tenant_applications, payments, cron_jobs

models.Base.metadata.create_all(bind=engine)

current_file = Path(__file__)
current_file_dir = current_file.parent
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
static_root_absolute = project_root_absolute /"app"/"static"


# def send_rent_notifications():
#     while True:
#         db = SessionLocal()  # Create a new session for the thread
#         try:
#             utils.check_rent_due_dates(db)
#         finally:
#             db.close()
#         time.sleep(86400)  # Sleep for 24 hours

# def start_background_thread():
#     thread = threading.Thread(target=send_rent_notifications)
#     thread.start()

app = FastAPI()
app.mount('/static', StaticFiles(directory="static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# @app.on_event("startup")
# def startup_event():
#     start_background_thread()


@app.get('/')
def main():
    return{"message": "rental api"}



settings = config.Settings()


app.include_router(users.router)
app.include_router(property.router)
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(bookings.router)
app.include_router(maintenance_requests.router)
app.include_router(tenant_applications.router)
app.include_router(payments.router)
app.include_router(cron_jobs.router)

add_pagination(app)
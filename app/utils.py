from passlib.hash import bcrypt
import os
from fastapi import Depends, UploadFile, HTTPException
from pathlib import Path
from typing import Optional, List
import uuid
import time
import string
import secrets
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import credentials
import datetime
from . import database, models
from sqlalchemy.orm import Session


def send_rent_notification(recipient_email: str, recipient_name: str, days_until_due: int, property: str):
    sender_email = credentials.email_addr
    sender_password = credentials.app_password
    
    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Reminder: Rent due in {days_until_due} day{'s' if days_until_due > 1 else ''}"
    
    # Body of the email
    body = f"Dear {recipient_name},\n\nThis is a reminder that your rent is due in {days_until_due} day{'s' if days_until_due > 1 else ''} for property at {property}. Please make sure to complete the payment by the due date.\n\nThank you!"
    message.attach(MIMEText(body, "plain"))

    # Set up the SMTP server
    smtp_host = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Log in to the server and send email
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


# def check_rent_due_dates(db: Session):
#     # Example list of tenants with rent due dates
#     payments = db.query(models.Payment).all()
#     # Get today's date
#     today = datetime.datetime.now().date()

#     for payment in payments:
#         due_date = payment.due_date

#         # Calculate the number of days until the due date
#         days_until_due = (due_date - today).days

#         # Check if it's 3, 2, or 1 day(s) before the due date
#         if days_until_due in [3, 2, 1]:
#             tenant = db.query(models.Tenant).filter_by(id=payment.tenant_id).first()
#             prop = db.query(models.Property).filter_by(id=payment.property_id).first()

#             send_rent_notification(tenant.email, tenant.first_name, days_until_due, prop.address)



# Function to generate a random OTP
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


# Function to send email using smtplib
def send_email(recipient_email: str, otp: str):
    sender_email = credentials.email_addr
    sender_password = credentials.app_password
    
    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "Rently - Your OTP Code"
    
    # Body of the email
    body = f"Your OTP code is: {otp}"
    message.attach(MIMEText(body, "plain"))

    # Set up the SMTP server
    smtp_host = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Log in to the server and send email
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")



def hash_pwd(pwd):
    return bcrypt.hash(pwd)

def verify_pwd(pwd, hashed_pwd):
    return bcrypt.verify(pwd, hashed_pwd)


def allowed_file(filename: str, allowed) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed


def get_unique_filename(filename: str) -> str:
    ext = filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    timestamp = int(time.time())
    unique_filename = f"{unique_id}_{timestamp}.{ext}"
    return unique_filename


def save_pic(file: UploadFile, allowed_exts, upload_path: str) -> Optional[str]:
    if file:
        if not allowed_file(file.filename, allowed_exts):
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        unique_filename = get_unique_filename(file.filename)
        file_path = upload_path / unique_filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        return str(file_path)
    return None


def save_files(files: List[UploadFile], allowed_exts, upload_path: str) -> List[str]:
    if len(files) > 3:
        raise HTTPException(status_code=400, detail="Cannot upload more than 3 files")

    file_paths = []
    
    for file in files:
        if not allowed_file(file.filename, allowed_exts):
            raise HTTPException(status_code=400, detail=f"File type not allowed: {file.filename}")

        file_path = upload_path / file.filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        file_paths.append(str(file_path))
    
    return file_paths
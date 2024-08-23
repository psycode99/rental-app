from fastapi import APIRouter, Depends, status
from app.database import get_db
from app.utils import send_rent_notification
from app import models
import datetime
from sqlalchemy.orm import Session


router = APIRouter(prefix='/v1/cron_jobs',
                   tags=["Cron Jobs"])


@router.post('/rent_due', status_code=status.HTTP_200_OK)
def check_rent_due_dates(db: Session = Depends(get_db)):
    # Example list of tenants with rent due dates
    payments = db.query(models.Payment).all()
    # Get today's date
    today = datetime.datetime.now().date()

    for payment in payments:
        due_date = payment.due_date

        # Calculate the number of days until the due date
        days_until_due = (due_date - today).days

        # Check if it's 3, 2, or 1 day(s) before the due date
        if days_until_due in [3, 2, 1]:
            tenant = db.query(models.Tenant).filter_by(id=payment.tenant_id).first()
            prop = db.query(models.Property).filter_by(id=payment.property_id).first()

            send_rent_notification(tenant.email, tenant.first_name, days_until_due, prop.address)


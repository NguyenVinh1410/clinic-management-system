from fastapi import FastAPI

from app.config.settings import settings
from app.routers import (
    auth,
    patient,
    user,
    specialty,
    doctor,
    working_schedule,
    appointment,
    medical_record,
    medicine,
    prescription,
    invoice,
)

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env
    }


app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(user.router)
app.include_router(specialty.router)
app.include_router(doctor.router)
app.include_router(working_schedule.router)
app.include_router(appointment.router)
app.include_router(medical_record.router)
app.include_router(medicine.router)
app.include_router(prescription.router)
app.include_router(invoice.router)

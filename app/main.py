from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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
    medical_history,
    dashboard,
    web,
    chat
)

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.mount(
    "/static",
    StaticFiles(directory=settings.static_dir),
    name="static",
)


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
app.include_router(medical_history.router)
app.include_router(medical_history.doctor_router)
app.include_router(dashboard.router)
app.include_router(chat.router)

app.include_router(web.router)


from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config.settings import settings

templates = Jinja2Templates(directory=settings.templates_dir)

router = APIRouter(
    tags=["Web"]
)

@router.get(
    "/patient/dashboard",
    include_in_schema=False,
)
def patient_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient/dashboard.html",
        context={},
    )

@router.get(
    "/patient/doctors",
    include_in_schema=False,
)
def patient_doctors(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient/doctors.html",
        context={},
    )

@router.get(
    "/patient/doctors/{doctor_id}",
    include_in_schema=False,
)
def patient_doctor_detail(
        request: Request,
        doctor_id: int,
):
    return templates.TemplateResponse(
        request=request,
        name="patient/doctor-detail.html",
        context={"doctor_id": doctor_id},
    )

@router.get(
    "/patient/appointments",
    include_in_schema=False,
)
def patient_appointments(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient/appointments.html",
        context={},
    )

@router.get(
    "/patient/book-appointment",
    include_in_schema=False,
)
def patient_book_appointment(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient/book-appointment.html",
        context={},
    )

@router.get(
    "/patient/invoices",
    include_in_schema=False,
)
def patient_invoices(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient/invoices.html",
        context={},
    )

@router.get(
    "/patient/profile",
    include_in_schema=False,
)
def patient_profile(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient/profile.html",
        context={},
    )

@router.get(
    "/patient/medical-history",
    include_in_schema=False,
)
def patient_medical_history(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patient/medical-history.html",
        context={},
    )

@router.get(
    "/receptionist/dashboard",
    include_in_schema=False,
)
def receptionist_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="receptionist/dashboard.html",
        context={},
    )

@router.get(
    "/receptionist/patients",
    include_in_schema=False,
)
def receptionist_patients(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="receptionist/patients.html",
        context={},
    )

@router.get(
    "/receptionist/appointments",
    include_in_schema=False,
)
def receptionist_appointments(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="receptionist/appointments.html",
        context={},
    )

@router.get(
    "/receptionist/checkin",
    include_in_schema=False,
)
def receptionist_checkin(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="receptionist/checkin.html",
        context={},
    )

@router.get(
    "/receptionist/invoices",
    include_in_schema=False,
)
def receptionist_invoices(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="receptionist/invoices.html",
        context={},
    )

@router.get(
    "/doctor/dashboard",
    include_in_schema=False,
)
def doctor_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="doctor/dashboard.html",
        context={},
    )

@router.get(
    "/doctor/examination/{appointment_id}",
    include_in_schema=False,
)
def doctor_examination(request: Request, appointment_id: int):
    return templates.TemplateResponse(
        request=request,
        name="doctor/examination.html",
        context={"appointment_id": appointment_id},
    )

@router.get(
    "/",
    include_in_schema=False,
)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={},
    )

@router.get(
    "/register",
    include_in_schema=False,
)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={},
    )

@router.get(
    "/login",
    include_in_schema=False,
)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={},
    )

@router.get(
    "/dashboard",
    include_in_schema=False,
)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={},
    )


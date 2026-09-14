import re

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import AppointmentStatus, UserStatus, WorkingScheduleStatus
from app.models.user import Doctor
from app.models.specialty import Specialty
from app.models.working_schedule import WorkingSchedule
from app.services.appointment_service import AppointmentService


class AIIntent:
    FIND_DOCTOR = "find_doctor"
    FIND_SPECIALTY = "find_specialty"
    WORKING_HOURS = "working_hours"
    MY_APPOINTMENTS = "my_appointments"
    PROCESS_GUIDANCE = "process_guidance"
    UNKNOWN = "unknown"


class AIService:

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.strip().lower()

        text = (
            text
            .replace("đ", "d")
            .replace("á", "a")
            .replace("à", "a")
            .replace("ả", "a")
            .replace("ã", "a")
            .replace("ạ", "a")
            .replace("ă", "a")
            .replace("ắ", "a")
            .replace("ằ", "a")
            .replace("ẳ", "a")
            .replace("ẵ", "a")
            .replace("ặ", "a")
            .replace("â", "a")
            .replace("ấ", "a")
            .replace("ầ", "a")
            .replace("ẩ", "a")
            .replace("ẫ", "a")
            .replace("ậ", "a")
            .replace("é", "e")
            .replace("è", "e")
            .replace("ẻ", "e")
            .replace("ẽ", "e")
            .replace("ẹ", "e")
            .replace("ê", "e")
            .replace("ế", "e")
            .replace("ề", "e")
            .replace("ể", "e")
            .replace("ễ", "e")
            .replace("ệ", "e")
            .replace("í", "i")
            .replace("ì", "i")
            .replace("ỉ", "i")
            .replace("ĩ", "i")
            .replace("ị", "i")
            .replace("ó", "o")
            .replace("ò", "o")
            .replace("ỏ", "o")
            .replace("õ", "o")
            .replace("ọ", "o")
            .replace("ô", "o")
            .replace("ố", "o")
            .replace("ồ", "o")
            .replace("ổ", "o")
            .replace("ỗ", "o")
            .replace("ộ", "o")
            .replace("ơ", "o")
            .replace("ớ", "o")
            .replace("ờ", "o")
            .replace("ở", "o")
            .replace("ỡ", "o")
            .replace("ợ", "o")
            .replace("ú", "u")
            .replace("ù", "u")
            .replace("ủ", "u")
            .replace("ũ", "u")
            .replace("ụ", "u")
            .replace("ư", "u")
            .replace("ứ", "u")
            .replace("ừ", "u")
            .replace("ử", "u")
            .replace("ữ", "u")
            .replace("ự", "u")
            .replace("ý", "y")
            .replace("ỳ", "y")
            .replace("ỷ", "y")
            .replace("ỹ", "y")
            .replace("ỵ", "y")
        )

        return re.sub(r"\s+", " ", text)


    @staticmethod
    def detect_intent(message: str) -> str:
        text = AIService.normalize_text(message)

        if any(
            keyword in text
            for keyword in [
                "xem lich cua toi",
                "lich kham cua toi",
                "toi co lich nao",
                "lich hen cua toi",
                "lich kham toi",
            ]
        ):
            return AIIntent.MY_APPOINTMENTS

        if any(
            keyword in text
            for keyword in [
                "gio lam viec",
                "lich lam viec",
                "bac si lam viec",
                "bac si lam luc nao",
                "khi nao bac si lam",
            ]
        ):
            return AIIntent.WORKING_HOURS

        if any(
            keyword in text
            for keyword in [
                "chuyen khoa",
                "co nhung khoa nao",
                "benh vien co khoa nao",
            ]
        ):
            return AIIntent.FIND_SPECIALTY

        if any(
            keyword in text
            for keyword in [
                "tim bac si",
                "tim bs",
                "bac si nao",
                "co bac si",
                "danh sach bac si",
            ]
        ):
            return AIIntent.FIND_DOCTOR

        if any(
            keyword in text
            for keyword in [
                "quy trinh",
                "huong dan",
                "lam thu tuc",
                "thu tuc kham",
                "kham nhu the nao",
            ]
        ):
            return AIIntent.PROCESS_GUIDANCE

        return AIIntent.UNKNOWN


    @staticmethod
    def handle_message(
        db: Session,
        patient_id: int,
        message: str,
    ) -> tuple[str, str]:

        intent = AIService.detect_intent(message)

        if intent == AIIntent.FIND_SPECIALTY:
            reply = AIService.find_specialties(db)

        elif intent == AIIntent.FIND_DOCTOR:
            reply = AIService.find_doctors(db, message)

        elif intent == AIIntent.WORKING_HOURS:
            reply = AIService.find_working_hours(db, message)

        elif intent == AIIntent.MY_APPOINTMENTS:
            reply = AIService.get_my_appointments(
                db=db,
                patient_id=patient_id,
            )

        elif intent == AIIntent.PROCESS_GUIDANCE:
            reply = AIService.process_guidance()

        else:
            intent = AIIntent.UNKNOWN
            reply = AIService.unknown_reply()

        return intent, reply


    @staticmethod
    def find_specialties(
        db: Session,
    ) -> str:

        stmt = (
            select(Specialty)
            .order_by(Specialty.name)
        )

        specialties = (
            db.execute(stmt)
            .scalars()
            .all()
        )

        if not specialties:
            return "Hiện chưa có thông tin chuyên khoa."

        names = [
            specialty.name
            for specialty in specialties
        ]

        return (
            "Hiện phòng khám có các chuyên khoa: "
            + ", ".join(names)
            + "."
        )


    @staticmethod
    def find_doctors(
        db: Session,
        message: str,
    ) -> str:

        text = AIService.normalize_text(message)

        stmt = (
            select(Doctor)
            .options(
                joinedload(Doctor.specialty)
            )
            .where(
                Doctor.status == UserStatus.ACTIVE
            )
            .order_by(Doctor.full_name)
        )

        doctors = (
            db.execute(stmt)
            .scalars()
            .all()
        )

        if not doctors:
            return "Hiện chưa có bác sĩ đang hoạt động."

        matched_doctors = []

        for doctor in doctors:

            doctor_name = AIService.normalize_text(
                doctor.full_name
            )

            specialty_name = (
                AIService.normalize_text(
                    doctor.specialty.name
                )
                if doctor.specialty
                else ""
            )

            if (
                doctor_name in text
                or specialty_name in text
            ):
                matched_doctors.append(doctor)

        if matched_doctors:
            doctors = matched_doctors

        lines = []

        for doctor in doctors[:10]:

            specialty = (
                doctor.specialty.name
                if doctor.specialty
                else "Chưa cập nhật"
            )

            lines.append(
                f"- {doctor.full_name} - {specialty}"
            )

        return (
            "Tôi tìm thấy các bác sĩ sau:\n"
            + "\n".join(lines)
        )


    @staticmethod
    def find_working_hours(
        db: Session,
        message: str,
    ) -> str:

        text = AIService.normalize_text(message)

        stmt = (
            select(WorkingSchedule)
            .options(
                joinedload(
                    WorkingSchedule.doctor
                )
                .joinedload(
                    Doctor.specialty
                )
            )
            .where(
                WorkingSchedule.status == WorkingScheduleStatus.ACTIVE
            )
            .order_by(
                WorkingSchedule.work_date,
                WorkingSchedule.start_time,
            )
        )

        schedules = (
            db.execute(stmt)
            .scalars()
            .all()
        )

        if not schedules:
            return "Hiện chưa có lịch làm việc."

        matched = []

        for schedule in schedules:

            doctor = schedule.doctor

            doctor_name = AIService.normalize_text(
                doctor.full_name
            )

            specialty_name = (
                AIService.normalize_text(
                    doctor.specialty.name
                )
                if doctor.specialty
                else ""
            )

            if (
                doctor_name in text
                or specialty_name in text
            ):
                matched.append(schedule)

        if matched:
            schedules = matched

        lines = []

        for schedule in schedules[:10]:

            doctor_name = (
                schedule.doctor.full_name
            )

            lines.append(
                f"- {doctor_name}: "
                f"{schedule.work_date.strftime('%d/%m/%Y')} "
                f"{schedule.start_time.strftime('%H:%M')}"
                f"-{schedule.end_time.strftime('%H:%M')}"
            )

        return (
            "Lịch làm việc tôi tìm thấy:\n"
            + "\n".join(lines)
        )


    @staticmethod
    def get_my_appointments(
        db: Session,
        patient_id: int,
    ) -> str:

        appointments = (
            AppointmentService
            .get_appointments_by_patient(
                db=db,
                patient_id=patient_id,
            )
        )

        active_appointments = [
            appointment
            for appointment in appointments
            if appointment["status"]
            in (
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED,
            )
        ]

        if not active_appointments:
            return "Bạn hiện không có lịch khám sắp tới."

        lines = []

        for appointment in active_appointments[:10]:

            time = appointment[
                "appointment_time"
            ]

            lines.append(
                f"- {time.strftime('%d/%m/%Y %H:%M')} - "
                f"{appointment['doctor_name']} - "
                f"{appointment['specialty_name']} - "
                f"{appointment['status'].value}"
            )

        return (
            "Lịch khám sắp tới của bạn:\n"
            + "\n".join(lines)
        )


    @staticmethod
    def process_guidance() -> str:
        return (
            "Quy trình khám cơ bản:\n"
            "1. Chọn chuyên khoa hoặc bác sĩ.\n"
            "2. Chọn ngày và khung giờ còn trống.\n"
            "3. Đặt lịch khám.\n"
            "4. Đến phòng khám và làm thủ tục tiếp nhận.\n"
            "5. Bác sĩ thăm khám.\n"
            "6. Xem thông tin hóa đơn và thanh toán."
        )


    @staticmethod
    def unknown_reply() -> str:
        return (
            "Tôi có thể hỗ trợ bạn các việc sau: "
            "tìm bác sĩ, xem chuyên khoa, "
            "xem lịch làm việc, xem lịch khám "
            "và hướng dẫn quy trình khám. "
            "Tôi không hỗ trợ chẩn đoán bệnh hoặc kê đơn."
        )
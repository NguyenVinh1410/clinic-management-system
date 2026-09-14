import re
from datetime import datetime, date, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.schemas.ai import AICommand
from app.services.llm_service import LLMService

from app.models.enums import AppointmentStatus, UserStatus, WorkingScheduleStatus
from app.models.user import Doctor
from app.models.appointment import Appointment
from app.models.specialty import Specialty
from app.models.working_schedule import WorkingSchedule
from app.services.appointment_service import AppointmentService
from app.core.exceptions import BusinessException, ConflictException, NotFoundException


class AIIntent:
    GREETING = "greeting"
    FIND_DOCTOR = "find_doctor"
    FIND_SPECIALTY = "find_specialty"
    WORKING_HOURS = "working_hours"
    FIND_AVAILABLE_SLOTS = "find_available_slots"
    BOOK_APPOINTMENT = "book_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
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
    def detect_intent(
            message: str,
    ) -> str:

        text = AIService.normalize_text(
            message
        )

        # =========================
        # GREETING
        # =========================

        if any(
                keyword in text
                for keyword in [
                    "xin chao",
                    "chao",
                    "hello",
                    "hi",
                    "alo",
                ]
        ):
            return AIIntent.GREETING

        # =========================
        # CANCEL APPOINTMENT
        # =========================

        if any(
                keyword in text
                for keyword in [
                    "huy lich",
                    "huy lich kham",
                    "huy hen",
                    "huy lich hen",
                    "khong muon kham nua",
                    "bo lich",
                ]
        ):
            return AIIntent.CANCEL_APPOINTMENT

        # =========================
        # BOOK APPOINTMENT
        # =========================

        if any(
                keyword in text
                for keyword in [
                    "dat lich",
                    "dat lich kham",
                    "dat cho toi",
                    "cho toi dat",
                    "toi muon dat",
                    "toi muon kham",
                    "dat cho minh",
                    "book lich",
                ]
        ):
            return AIIntent.BOOK_APPOINTMENT

        # =========================
        # MY APPOINTMENTS
        # =========================

        if any(
                keyword in text
                for keyword in [
                    "xem lich cua toi",
                    "lich kham cua toi",
                    "toi co lich nao",
                    "lich hen cua toi",
                    "lich kham toi",
                    "lich cua toi",
                ]
        ):
            return AIIntent.MY_APPOINTMENTS

        # =========================
        # AVAILABLE SLOTS
        # =========================

        if any(
                keyword in text
                for keyword in [
                    "gio trong",
                    "khung gio trong",
                    "lich trong",
                    "con gio nao",
                    "con khung gio nao",
                    "gio nao con trong",
                    "dat lich vao gio nao",
                ]
        ):
            return AIIntent.FIND_AVAILABLE_SLOTS

        # =========================
        # WORKING HOURS
        # =========================

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

        # =========================
        # SPECIALTY
        # =========================

        if any(
                keyword in text
                for keyword in [
                    "chuyen khoa",
                    "co nhung khoa nao",
                    "benh vien co khoa nao",
                ]
        ):
            return AIIntent.FIND_SPECIALTY

        # =========================
        # DOCTOR
        # =========================

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

        # =========================
        # PROCESS
        # =========================

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
            chat_session_id: int,
            message: str,
    ) -> tuple[str, str]:

        # =========================
        # GIBBERISH
        # =========================

        if AIService.is_gibberish(
                message
        ):
            return (
                AIIntent.UNKNOWN,
                AIService.unknown_reply(),
            )

        intent = AIService.detect_intent(
            message
        )

        # =========================
        # GREETING
        # =========================

        if intent == AIIntent.GREETING:

            reply = (
                "Xin chào! Tôi là AI Assistant "
                "của phòng khám.\n"
                "Tôi có thể hỗ trợ bạn:\n"
                "- Tìm bác sĩ\n"
                "- Xem chuyên khoa\n"
                "- Xem lịch làm việc\n"
                "- Xem giờ trống\n"
                "- Đặt lịch khám\n"
                "- Hủy lịch khám\n"
                "- Xem lịch khám của bạn\n"
                "- Hướng dẫn quy trình khám"
            )

        # =========================
        # FIND SPECIALTY
        # =========================

        elif intent == AIIntent.FIND_SPECIALTY:

            reply = (
                AIService.find_specialties(
                    db
                )
            )

        # =========================
        # FIND DOCTOR
        # =========================

        elif intent == AIIntent.FIND_DOCTOR:

            reply = (
                AIService.find_doctors(
                    db,
                    message,
                )
            )

        # =========================
        # WORKING HOURS
        # =========================

        elif intent == AIIntent.WORKING_HOURS:

            reply = (
                AIService.find_working_hours(
                    db,
                    message,
                )
            )

        # =========================
        # AVAILABLE SLOTS
        # =========================

        elif intent == AIIntent.FIND_AVAILABLE_SLOTS:

            reply = (
                AIService.find_available_slots(
                    db=db,
                    message=message,
                )
            )

        # =========================
        # BOOK APPOINTMENT
        # =========================

        elif intent == AIIntent.BOOK_APPOINTMENT:

            reply = (
                AIService.book_appointment(
                    db=db,
                    patient_id=patient_id,
                    chat_session_id=chat_session_id,
                    message=message,
                )
            )

        # =========================
        # CANCEL APPOINTMENT
        # =========================

        elif intent == AIIntent.CANCEL_APPOINTMENT:

            reply = (
                AIService.cancel_appointment(
                    db=db,
                    patient_id=patient_id,
                    message=message,
                )
            )

        # =========================
        # MY APPOINTMENTS
        # =========================

        elif intent == AIIntent.MY_APPOINTMENTS:

            reply = (
                AIService.get_my_appointments(
                    db=db,
                    patient_id=patient_id,
                )
            )

        # =========================
        # PROCESS GUIDANCE
        # =========================

        elif intent == AIIntent.PROCESS_GUIDANCE:

            reply = (
                AIService.process_guidance()
            )

        # =========================
        # UNKNOWN
        # =========================

        else:

            intent = AIIntent.UNKNOWN

            reply = (
                AIService.unknown_reply()
            )

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
    def find_doctor_from_message(
            db: Session,
            message: str,
    ) -> Doctor | None:

        text = AIService.normalize_text(
            message
        )

        stmt = (
            select(Doctor)
            .options(
                joinedload(
                    Doctor.specialty
                )
            )
            .where(
                Doctor.status == UserStatus.ACTIVE
            )
        )

        doctors = (
            db.execute(stmt)
            .scalars()
            .all()
        )

        for doctor in doctors:

            doctor_name = AIService.normalize_text(
                doctor.full_name
            )

            name_parts = doctor_name.split()

            if doctor_name in text:
                return doctor

            if (
                    len(name_parts) >= 2
                    and name_parts[-1] in text
            ):
                return doctor

        return None

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
    def find_available_slots(
            db: Session,
            message: str,
    ) -> str:

        doctor = (
            AIService.find_doctor_from_message(
                db,
                message,
            )
        )

        if doctor is None:
            return (
                "Bạn vui lòng cho tôi biết tên bác sĩ "
                "mà bạn muốn xem lịch."
            )

        work_date = (
            AIService.extract_date(
                message
            )
        )

        if work_date is None:
            return (
                "Bạn vui lòng cho tôi biết ngày muốn khám. "
                "Ví dụ: hôm nay, ngày mai hoặc 17/09."
            )

        if work_date < date.today():
            return (
                "Ngày khám không được ở trong quá khứ. "
                "Bạn vui lòng chọn ngày khác."
            )

        available_slots = (
            AIService.get_available_slots(
                db=db,
                doctor_id=doctor.user_id,
                work_date=work_date,
            )
        )

        if not available_slots:
            return (
                f"Bác sĩ {doctor.full_name} "
                f"không còn khung giờ trống "
                f"ngày {work_date.strftime('%d/%m/%Y')}."
            )

        return (
                f"Bác sĩ {doctor.full_name} "
                f"còn các khung giờ trống ngày "
                f"{work_date.strftime('%d/%m/%Y')}:\n"
                + "\n".join(
            f"- {slot}"
            for slot in available_slots
        )
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
            appointment_time = (
                appointment["appointment_time"]
            )

            lines.append(
                f"- Mã lịch: "
                f"{appointment['appointment_id']}\n"
                f"  Bác sĩ: "
                f"{appointment['doctor_name']}\n"
                f"  Chuyên khoa: "
                f"{appointment['specialty_name']}\n"
                f"  Thời gian: "
                f"{appointment_time.strftime('%d/%m/%Y %H:%M')}\n"
                f"  Trạng thái: "
                f"{appointment['status'].value}"
            )

        return (
            "Lịch khám sắp tới của bạn:\n\n"
            + "\n\n".join(lines)
        )

    @staticmethod
    def process_guidance() -> str:

        return (
            "Quy trình khám tại phòng khám:\n\n"
            "1. Chọn chuyên khoa hoặc bác sĩ.\n"
            "2. Chọn ngày khám.\n"
            "3. Chọn khung giờ còn trống 30 phút.\n"
            "4. Đặt lịch khám.\n"
            "5. Đến phòng khám làm thủ tục tiếp nhận.\n"
            "6. Bác sĩ thực hiện thăm khám.\n"
            "7. Xem hóa đơn và thực hiện thanh toán."
        )

    @staticmethod
    def is_gibberish(
            message: str,
    ) -> bool:

        text = (
            AIService.normalize_text(
                message
            )
        )

        if not text:
            return True

        if len(text) < 2:
            return True

        if not any(
                char.isalpha()
                for char in text
        ):
            return True

        return False

    @staticmethod
    def unknown_reply() -> str:

        return (
            "Xin lỗi, tôi chưa hiểu hoặc yêu cầu này "
            "nằm ngoài phạm vi hỗ trợ của tôi.\n\n"
            "Tôi có thể giúp bạn:\n"
            "• Tìm bác sĩ\n"
            "• Xem chuyên khoa\n"
            "• Xem lịch làm việc\n"
            "• Xem giờ trống\n"
            "• Đặt lịch khám\n"
            "• Hủy lịch khám\n"
            "• Xem lịch khám của bạn\n"
            "• Hướng dẫn quy trình khám\n\n"
            "Tôi không hỗ trợ chẩn đoán bệnh "
            "hoặc kê đơn thuốc."
        )

    @staticmethod
    def get_available_slots(
            db: Session,
            doctor_id: int,
            work_date: date,
    ) -> list[str]:

        schedule_stmt = (
            select(WorkingSchedule)
            .where(
                WorkingSchedule.doctor_id == doctor_id,
                WorkingSchedule.work_date == work_date,
                WorkingSchedule.status
                == WorkingScheduleStatus.ACTIVE,
            )
            .order_by(
                WorkingSchedule.start_time
            )
        )

        schedules = (
            db.execute(schedule_stmt)
            .scalars()
            .all()
        )

        if not schedules:
            return []

        appointment_stmt = (
            select(Appointment)
            .join(
                WorkingSchedule,
                Appointment.schedule_id
                == WorkingSchedule.schedule_id,
            )
            .where(
                WorkingSchedule.doctor_id == doctor_id,
                WorkingSchedule.work_date == work_date,
                Appointment.status.in_(
                    [
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED,
                    ]
                ),
            )
        )

        appointments = (
            db.execute(appointment_stmt)
            .scalars()
            .all()
        )

        booked_times = {
            appointment.appointment_time
            for appointment in appointments
        }

        available_slots = []

        for schedule in schedules:

            current_time = schedule.start_time

            while True:

                slot_end = (
                        datetime.combine(
                            work_date,
                            current_time,
                        )
                        + timedelta(minutes=30)
                ).time()

                if slot_end > schedule.end_time:
                    break

                slot_datetime = datetime.combine(
                    work_date,
                    current_time,
                )

                now = datetime.now()

                if (
                        work_date == now.date()
                        and slot_datetime <= now
                ):
                    current_time = (
                            datetime.combine(
                                work_date,
                                current_time,
                            )
                            + timedelta(minutes=30)
                    ).time()

                    continue

                if (
                        slot_datetime
                        not in booked_times
                ):
                    available_slots.append(
                        current_time.strftime("%H:%M")
                    )

                current_time = (
                        datetime.combine(work_date, current_time)
                        + timedelta(minutes=30)
                ).time()

        return available_slots

    @staticmethod
    def extract_date(
            message: str,
    ) -> date | None:

        text = AIService.normalize_text(
            message
        )

        today = date.today()

        if "hom nay" in text:
            return today

        if "ngay mai" in text:
            return today + timedelta(days=1)

        match = re.search(
            r"(\d{1,2})[\/\-](\d{1,2})",
            text,
        )

        if match:

            day = int(match.group(1))
            month = int(match.group(2))

            try:
                return date(
                    today.year,
                    month,
                    day,
                )
            except ValueError:
                return None

        return None

    @staticmethod
    def extract_time(
            message: str,
    ) -> time | None:

        text = AIService.normalize_text(
            message
        )

        patterns = [
            r"\b(\d{1,2})[:h](\d{2})\b",
            r"\b(\d{1,2})\s*gio\s*(\d{1,2})?\b",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
            )

            if not match:
                continue

            hour = int(
                match.group(1)
            )

            minute = (
                int(match.group(2))
                if match.group(2)
                else 0
            )

            if (
                    0 <= hour <= 23
                    and 0 <= minute <= 59
            ):
                return time(
                    hour=hour,
                    minute=minute,
                )

        return None

    @staticmethod
    def book_appointment(
            db: Session,
            patient_id: int,
            chat_session_id: int,
            message: str,
    ) -> str:

        doctor = (
            AIService.find_doctor_from_message(
                db,
                message,
            )
        )

        if doctor is None:
            return (
                "Bạn vui lòng cho tôi biết tên bác sĩ "
                "muốn đặt lịch."
            )

        work_date = (
            AIService.extract_date(
                message
            )
        )

        if work_date is None:
            return (
                "Bạn vui lòng cho tôi biết ngày muốn khám. "
                "Ví dụ: ngày mai hoặc 17/09."
            )

        if work_date < date.today():
            return (
                "Ngày khám không được ở trong quá khứ. "
                "Bạn vui lòng chọn ngày khác."
            )

        appointment_time = (
            AIService.extract_time(
                message
            )
        )

        if appointment_time is None:
            return (
                "Bạn vui lòng cho tôi biết giờ muốn khám. "
                "Ví dụ: 08:00, 08:30 hoặc 09:00."
            )

        if appointment_time.minute not in (0, 30):
            return (
                "Giờ khám phải theo khung 30 phút. "
                "Ví dụ: 08:00, 08:30, 09:00."
            )

        schedule_stmt = (
            select(WorkingSchedule)
            .where(
                WorkingSchedule.doctor_id
                == doctor.user_id,

                WorkingSchedule.work_date
                == work_date,

                WorkingSchedule.status
                == WorkingScheduleStatus.ACTIVE,
            )
            .order_by(
                WorkingSchedule.start_time
            )
        )

        schedules = (
            db.execute(schedule_stmt)
            .scalars()
            .all()
        )

        if not schedules:
            return (
                f"Bác sĩ {doctor.full_name} "
                f"không có ca làm việc vào "
                f"{work_date.strftime('%d/%m/%Y')}."
            )

        appointment_datetime = datetime.combine(
            work_date,
            appointment_time,
        )

        selected_schedule = None

        for schedule in schedules:

            schedule_start = datetime.combine(
                schedule.work_date,
                schedule.start_time,
            )

            schedule_end = datetime.combine(
                schedule.work_date,
                schedule.end_time,
            )

            appointment_end = (
                    appointment_datetime
                    + timedelta(minutes=30)
            )

            if (
                    appointment_datetime >= schedule_start
                    and appointment_end <= schedule_end
            ):
                selected_schedule = schedule
                break

        if selected_schedule is None:
            return (
                f"Khung giờ "
                f"{appointment_time.strftime('%H:%M')} "
                f"không nằm trong ca làm việc của "
                f"bác sĩ {doctor.full_name}."
            )

        try:

            AppointmentService.create_appointment_by_ai(
                db=db,
                patient_id=patient_id,
                schedule_id=selected_schedule.schedule_id,
                appointment_time=appointment_datetime,
                chat_session_id=chat_session_id,
            )

        except (BusinessException, ConflictException) as exc:

            return str(exc)

        return (
            "Đặt lịch khám thành công.\n"
            f"Bác sĩ: {doctor.full_name}\n"
            f"Ngày: {work_date.strftime('%d/%m/%Y')}\n"
            f"Giờ: {appointment_time.strftime('%H:%M')}\n"
            "Thời lượng: 30 phút."
        )

    @staticmethod
    def extract_appointment_id(
            message: str,
    ) -> int | None:

        match = re.search(
            r"(?:lich|hen)?\s*(?:so|#)?\s*(\d+)",
            message.lower(),
        )

        if not match:
            return None

        return int(
            match.group(1)
        )

    @staticmethod
    def cancel_appointment(
            db: Session,
            patient_id: int,
            message: str,
    ) -> str:

        appointment_id = (
            AIService.extract_appointment_id(
                message
            )
        )

        if appointment_id is None:
            return (
                "Bạn vui lòng cho tôi biết mã lịch khám "
                "muốn hủy. Ví dụ: Hủy lịch số 25."
            )

        try:

            appointment = (
                AppointmentService
                .cancel_appointment_by_ai(
                    db=db,
                    appointment_id=appointment_id,
                    patient_id=patient_id,
                )
            )

        except (
                BusinessException,
                NotFoundException,
                ConflictException,
        ) as exc:

            return str(exc)

        return (
            "Đã hủy lịch khám thành công.\n"
            f"Mã lịch: {appointment.appointment_id}\n"
            f"Bác sĩ: {appointment.doctor_name}\n"
            f"Thời gian: "
            f"{appointment.appointment_time.strftime('%d/%m/%Y %H:%M')}"
        )

    @staticmethod
    def handle_llm_message(
            db: Session,
            patient_id: int,
            chat_session_id: int,
            message: str,
            history: list[dict],
    ) -> tuple[str, str]:

        try:

            command = LLMService.parse_message(
                message=message,
                history=history,
            )

        except RuntimeError as exc:

            return (
                AIIntent.UNKNOWN,
                str(exc),
            )

        intent = command.intent

        if intent == AIIntent.GREETING:
            return (
                intent,
                AIService.greeting_reply(),
            )

        if intent == AIIntent.FIND_SPECIALTY:
            return (
                intent,
                AIService.find_specialties(
                    db
                ),
            )

        if intent == AIIntent.FIND_DOCTOR:
            return (
                intent,
                AIService.find_doctors_by_command(
                    db=db,
                    command=command,
                ),
            )

        if intent == AIIntent.WORKING_HOURS:
            return (
                intent,
                AIService.find_working_hours_by_command(
                    db=db,
                    command=command,
                ),
            )

        if intent == AIIntent.FIND_AVAILABLE_SLOTS:
            return (
                intent,
                AIService.find_available_slots_by_command(
                    db=db,
                    command=command,
                ),
            )

        if intent == AIIntent.BOOK_APPOINTMENT:
            return (
                intent,
                AIService.book_appointment_by_command(
                    db=db,
                    patient_id=patient_id,
                    chat_session_id=chat_session_id,
                    command=command,
                ),
            )

        if intent == AIIntent.CANCEL_APPOINTMENT:
            return (
                intent,
                AIService.cancel_appointment_by_command(
                    db=db,
                    patient_id=patient_id,
                    command=command,
                ),
            )

        if intent == AIIntent.MY_APPOINTMENTS:
            return (
                intent,
                AIService.get_my_appointments(
                    db=db,
                    patient_id=patient_id,
                ),
            )

        if intent == AIIntent.PROCESS_GUIDANCE:
            return (
                intent,
                AIService.process_guidance(),
            )

        return (
            AIIntent.UNKNOWN,
            AIService.unknown_reply(),
        )

    @staticmethod
    def greeting_reply() -> str:

        return (
            "Xin chào! Tôi là AI Assistant "
            "của phòng khám.\n\n"
            "Tôi có thể hỗ trợ bạn:\n"
            "- Tìm bác sĩ\n"
            "- Xem chuyên khoa\n"
            "- Xem lịch làm việc\n"
            "- Xem giờ trống\n"
            "- Đặt lịch khám\n"
            "- Hủy lịch khám\n"
            "- Xem lịch khám của bạn\n"
            "- Hướng dẫn quy trình khám"
        )

    @staticmethod
    def find_doctors_by_command(
            db: Session,
            command: AICommand,
    ) -> str:

        if command.specialty_name:

            text = AIService.normalize_text(
                command.specialty_name
            )

            stmt = (
                select(Doctor)
                .options(
                    joinedload(
                        Doctor.specialty
                    )
                )
                .where(
                    Doctor.status == UserStatus.ACTIVE
                )
            )

            doctors = (
                db.execute(stmt)
                .scalars()
                .all()
            )

            matched = []

            for doctor in doctors:

                specialty_name = (
                    AIService.normalize_text(
                        doctor.specialty.name
                    )
                    if doctor.specialty
                    else ""
                )

                if text in specialty_name:
                    matched.append(doctor)

            if not matched:
                return (
                    "Tôi chưa tìm thấy bác sĩ "
                    "phù hợp với chuyên khoa bạn yêu cầu."
                )

            lines = []

            for doctor in matched[:10]:
                lines.append(
                    f"- {doctor.full_name} - "
                    f"{doctor.specialty.name}"
                )

            return (
                    "Tôi tìm thấy các bác sĩ:\n"
                    + "\n".join(lines)
            )

        return AIService.find_doctors(
            db,
            command.doctor_name or "",
        )

    @staticmethod
    def find_working_hours_by_command(
            db: Session,
            command: AICommand,
    ) -> str:

        if not command.doctor_name:
            return (
                "Bạn vui lòng cho tôi biết "
                "tên bác sĩ muốn xem lịch."
            )

        doctor = (
            AIService.find_doctor_from_text(
                db,
                command.doctor_name,
            )
        )

        if doctor is None:
            return (
                f"Tôi không tìm thấy bác sĩ "
                f"{command.doctor_name}."
            )

        stmt = (
            select(WorkingSchedule)
            .where(
                WorkingSchedule.doctor_id
                == doctor.user_id,

                WorkingSchedule.status
                == WorkingScheduleStatus.ACTIVE,
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
            return (
                f"Bác sĩ {doctor.full_name} "
                "hiện chưa có lịch làm việc."
            )

        lines = []

        for schedule in schedules[:10]:
            lines.append(
                f"- "
                f"{schedule.work_date.strftime('%d/%m/%Y')} "
                f"{schedule.start_time.strftime('%H:%M')}"
                f"-"
                f"{schedule.end_time.strftime('%H:%M')}"
            )

        return (
                f"Lịch làm việc của bác sĩ "
                f"{doctor.full_name}:\n"
                + "\n".join(lines)
        )

    @staticmethod
    def find_doctor_from_text(
            db: Session,
            doctor_name: str,
    ) -> Doctor | None:

        text = AIService.normalize_text(
            doctor_name
        )

        stmt = (
            select(Doctor)
            .options(
                joinedload(
                    Doctor.specialty
                )
            )
            .where(
                Doctor.status == UserStatus.ACTIVE
            )
        )

        doctors = (
            db.execute(stmt)
            .scalars()
            .all()
        )

        for doctor in doctors:

            normalized_name = (
                AIService.normalize_text(
                    doctor.full_name
                )
            )

            if text in normalized_name:
                return doctor

            parts = normalized_name.split()

            if parts and parts[-1] in text:
                return doctor

        return None

    @staticmethod
    def find_available_slots_by_command(
            db: Session,
            command: AICommand,
    ) -> str:

        if not command.doctor_name:
            return (
                "Bạn vui lòng cho tôi biết "
                "tên bác sĩ."
            )

        if not command.appointment_date:
            return (
                "Bạn vui lòng cho tôi biết "
                "ngày muốn khám."
            )

        if (
                command.appointment_date
                < date.today()
        ):
            return (
                "Ngày khám không được ở trong quá khứ."
            )

        doctor = (
            AIService.find_doctor_from_text(
                db,
                command.doctor_name,
            )
        )

        if doctor is None:
            return (
                f"Tôi không tìm thấy bác sĩ "
                f"{command.doctor_name}."
            )

        slots = (
            AIService.get_available_slots(
                db=db,
                doctor_id=doctor.user_id,
                work_date=command.appointment_date,
            )
        )

        if not slots:
            return (
                f"Bác sĩ {doctor.full_name} "
                f"không còn khung giờ trống "
                f"ngày "
                f"{command.appointment_date.strftime('%d/%m/%Y')}."
            )

        return (
                f"Bác sĩ {doctor.full_name} "
                f"còn các khung giờ ngày "
                f"{command.appointment_date.strftime('%d/%m/%Y')}:\n"
                + "\n".join(
            f"- {slot}"
            for slot in slots
        )
        )

    @staticmethod
    def book_appointment_by_command(
            db: Session,
            patient_id: int,
            chat_session_id: int,
            command: AICommand,
    ) -> str:

        if not command.doctor_name:
            return (
                "Bạn vui lòng cho tôi biết "
                "tên bác sĩ."
            )

        if not command.appointment_date:
            return (
                "Bạn vui lòng cho tôi biết "
                "ngày muốn khám."
            )

        if not command.appointment_time:
            return (
                "Bạn vui lòng cho tôi biết "
                "giờ muốn khám."
            )

        if (
                command.appointment_date
                < date.today()
        ):
            return (
                "Ngày khám không được ở trong quá khứ."
            )

        if command.appointment_time.minute not in (
                0,
                30,
        ):
            return (
                "Giờ khám phải theo khung 30 phút. "
                "Ví dụ: 08:00, 08:30 hoặc 09:00."
            )

        doctor = (
            AIService.find_doctor_from_text(
                db,
                command.doctor_name,
            )
        )

        if doctor is None:
            return (
                f"Tôi không tìm thấy bác sĩ "
                f"{command.doctor_name}."
            )

        schedule_stmt = (
            select(WorkingSchedule)
            .where(
                WorkingSchedule.doctor_id
                == doctor.user_id,

                WorkingSchedule.work_date
                == command.appointment_date,

                WorkingSchedule.status
                == WorkingScheduleStatus.ACTIVE,
            )
            .order_by(
                WorkingSchedule.start_time
            )
        )

        schedules = (
            db.execute(
                schedule_stmt
            )
            .scalars()
            .all()
        )

        if not schedules:
            return (
                f"Bác sĩ {doctor.full_name} "
                f"không có ca làm việc ngày "
                f"{command.appointment_date.strftime('%d/%m/%Y')}."
            )

        appointment_datetime = datetime.combine(
            command.appointment_date,
            command.appointment_time,
        )

        selected_schedule = None

        for schedule in schedules:

            start = datetime.combine(
                schedule.work_date,
                schedule.start_time,
            )

            end = datetime.combine(
                schedule.work_date,
                schedule.end_time,
            )

            appointment_end = (
                    appointment_datetime
                    + timedelta(minutes=30)
            )

            if (
                    appointment_datetime >= start
                    and appointment_end <= end
            ):
                selected_schedule = schedule
                break

        if selected_schedule is None:
            return (
                f"Khung giờ "
                f"{command.appointment_time.strftime('%H:%M')} "
                f"không nằm trong ca làm việc của "
                f"bác sĩ {doctor.full_name}."
            )

        try:

            appointment = (
                AppointmentService
                .create_appointment_by_ai(
                    db=db,
                    patient_id=patient_id,
                    schedule_id=(
                        selected_schedule.schedule_id
                    ),
                    appointment_time=(
                        appointment_datetime
                    ),
                    chat_session_id=chat_session_id,
                )
            )

        except (
                BusinessException,
                ConflictException,
                NotFoundException,
        ) as exc:

            return str(exc)

        return (
            "Đặt lịch khám thành công.\n"
            f"Mã lịch: {appointment.appointment_id}\n"
            f"Bác sĩ: {doctor.full_name}\n"
            f"Ngày: "
            f"{command.appointment_date.strftime('%d/%m/%Y')}\n"
            f"Giờ: "
            f"{command.appointment_time.strftime('%H:%M')}\n"
            "Thời lượng: 30 phút."
        )

    @staticmethod
    def cancel_appointment_by_command(
            db: Session,
            patient_id: int,
            command: AICommand,
    ) -> str:

        if command.appointment_id is None:
            return (
                "Bạn vui lòng cho tôi biết mã lịch khám "
                "muốn hủy. Ví dụ: Hủy lịch số 25."
            )

        try:

            appointment = (
                AppointmentService
                .cancel_appointment_by_ai(
                    db=db,
                    appointment_id=(
                        command.appointment_id
                    ),
                    patient_id=patient_id,
                )
            )

        except (
                BusinessException,
                ConflictException,
                NotFoundException,
        ) as exc:

            return str(exc)

        doctor = (
            appointment.schedule.doctor
        )

        return (
            "Đã hủy lịch khám thành công.\n"
            f"Mã lịch: {appointment.appointment_id}\n"
            f"Bác sĩ: {doctor.full_name}\n"
            f"Thời gian: "
            f"{appointment.appointment_time.strftime('%d/%m/%Y %H:%M')}"
        )
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, BusinessException
from app.models.chat import ChatMessage, ChatSession
from app.models.enums import ChatSenderType
from app.services.ai_service import AIService


class ChatService:

    @staticmethod
    def create_session(
        db: Session,
        patient_id: int,
    ) -> ChatSession:

        session = ChatSession(
            patient_id=patient_id,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session


    @staticmethod
    def get_session(
        db: Session,
        session_id: int,
        patient_id: int,
    ) -> ChatSession:

        stmt = (
            select(ChatSession)
            .where(
                ChatSession.session_id == session_id,
                ChatSession.patient_id == patient_id,
            )
        )

        session = (
            db.execute(stmt)
            .scalar_one_or_none()
        )

        if session is None:
            raise NotFoundException(
                "Khong tim thay phien tro chuyen"
            )

        return session


    @staticmethod
    def get_messages(
        db: Session,
        session: ChatSession,
    ) -> list[ChatMessage]:

        stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.session_id
                == session.session_id
            )
            .order_by(
                ChatMessage.created_at
            )
        )

        return (
            db.execute(stmt)
            .scalars()
            .all()
        )


    @staticmethod
    def send_message(
        db: Session,
        session: ChatSession,
        patient_id: int,
        content: str,
    ) -> tuple[str, str]:

        content = content.strip()

        if not content:
            raise BusinessException(
                "Noi dung tin nhan khong duoc de trong"
            )

        if len(content) > 2000:
            raise BusinessException(
                "Tin nhan khong duoc vuot qua 2000 ky tu"
            )

        patient_message = ChatMessage(
            session_id=session.session_id,
            sender_type=ChatSenderType.PATIENT,
            content=content,
            intent=None,
        )

        db.add(patient_message)
        db.flush()

        intent, reply = AIService.handle_message(
            db=db,
            patient_id=patient_id,
            message=content,
        )

        ai_message = ChatMessage(
            session_id=session.session_id,
            sender_type=ChatSenderType.AI,
            content=reply,
            intent=intent,
        )

        db.add(ai_message)
        db.commit()

        return intent, reply
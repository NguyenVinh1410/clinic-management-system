from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatResponse,
    ChatSessionResponse,
)
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/api/chat",
    tags=["AI Assistant"],
)


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    current_user: Annotated[
        User,
        Depends(
            requires_role(UserRole.PATIENT)
        ),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    return ChatService.create_session(
        db=db,
        patient_id=current_user.user_id,
    )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[ChatMessageResponse],
)
def get_messages(
    session_id: int,
    current_user: Annotated[
        User,
        Depends(
            requires_role(UserRole.PATIENT)
        ),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    session = ChatService.get_session(
        db=db,
        session_id=session_id,
        patient_id=current_user.user_id,
    )

    return ChatService.get_messages(
        db=db,
        session=session,
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    session_id: int,
    data: ChatMessageCreate,
    current_user: Annotated[
        User,
        Depends(
            requires_role(UserRole.PATIENT)
        ),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    session = ChatService.get_session(
        db=db,
        session_id=session_id,
        patient_id=current_user.user_id,
    )

    intent, reply = ChatService.send_message(
        db=db,
        session=session,
        patient_id=current_user.user_id,
        content=data.content,
    )

    return ChatResponse(
        session_id=session_id,
        intent=intent,
        reply=reply,
    )
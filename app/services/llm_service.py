from datetime import datetime
from zoneinfo import ZoneInfo

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    OpenAI,
)

from app.config.settings import settings
from app.schemas.ai import AICommand


VIETNAM_TZ = ZoneInfo(
    "Asia/Ho_Chi_Minh"
)


class LLMService:

    _client = OpenAI(
        base_url=settings.ollama_base_url,
        api_key="ollama",
        timeout=120.0,
        max_retries=0,
    )

    SYSTEM_PROMPT = """
    Bạn là AI Assistant của phòng khám.

    Chỉ hỗ trợ:
    - tìm bác sĩ
    - tìm chuyên khoa
    - xem lịch làm việc
    - xem giờ trống
    - đặt lịch
    - hủy lịch
    - xem lịch khám
    - hướng dẫn quy trình

    Không chẩn đoán bệnh.
    Không kê thuốc.
    Không tư vấn điều trị.

    Không tự bịa:
    - bác sĩ
    - chuyên khoa
    - ngày
    - giờ
    - appointment_id

    Nếu yêu cầu ngoài phạm vi hoặc không hiểu:
    intent = "unknown".

    Chỉ trả về đúng cấu trúc AICommand.
    """

    @classmethod
    def parse_message(
        cls,
        message: str,
        history: list[dict],
    ) -> AICommand:

        now = datetime.now(
            VIETNAM_TZ
        )

        current_date = (
            now.date().isoformat()
        )

        history_text = ""

        for item in history[-6:]:

            history_text += (
                f"{item['role']}: "
                f"{item['content']}\n"
            )

        user_input = f"""
Ngày hiện tại: {current_date}

Lịch sử hội thoại:
{history_text}

Tin nhắn mới:
{message}
"""

        try:

            completion = (
                cls._client
                .beta
                .chat
                .completions
                .parse(
                    model=settings.ollama_model,

                    messages=[
                        {
                            "role": "system",
                            "content": cls.SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": user_input,
                        },
                    ],

                    response_format=AICommand,

                    temperature=0,
                )
            )

        except (
            APITimeoutError,
            APIConnectionError,
            APIError,
        ) as exc:

            print("=" * 70)
            print("OLLAMA ERROR")
            print(
                "TYPE:",
                type(exc).__name__,
            )
            print(
                "MESSAGE:",
                str(exc),
            )
            print("=" * 70)

            raise RuntimeError(
                "Không thể kết nối Ollama. "
                "Hãy kiểm tra Ollama đang chạy."
            ) from exc

        message_result = (
            completion
            .choices[0]
            .message
        )

        parsed = (
            message_result.parsed
        )

        if parsed is None:

            raise RuntimeError(
                "Ollama không trả về dữ liệu "
                "đúng cấu trúc."
            )

        return parsed
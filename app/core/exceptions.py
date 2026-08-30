from fastapi import HTTPException, status

class BusinessException(HTTPException):
    def __init__(self, detail: str = "Yeu cau khong hop le"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Khong tim thay du lieu"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Chua xac thuc"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Khong co quyen truy cap"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class ConflictException(HTTPException):
    def __init__(self, detail: str = "Xung dot du lieu"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
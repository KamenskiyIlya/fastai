from datetime import datetime

from fastapi import APIRouter

from schemas import UserDetailsResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserDetailsResponse,
    summary="Получить учетные данные пользователя",
    response_description="Данные пользователя",
)
def get_user() -> UserDetailsResponse:
    return UserDetailsResponse(
        email="example@example.com",
        is_active=True,
        profile_id=1,
        registered_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updated_at=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        username="klol1k",
    )

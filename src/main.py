from datetime import datetime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, Field

app = FastAPI()


class UserDetailsResponse(BaseModel):
    profileId: int
    email: EmailStr
    username: str = Field(..., max_length=254)
    registeredAt: datetime
    updatedAt: datetime
    isActive: bool

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'email': 'example@example.com',
                'isActive': True,
                'profileId': '1',
                'registeredAt': '2025-06-15T18:29:56+00:00',
                'updatedAt': '2025-06-15T18:29:56+00:00',
                'username': 'user123',
            },
        },
    )


@app.get(
    "/users/me",
    response_model=UserDetailsResponse,
    summary='Получить учетные данные пользователя',
    response_description='Данные пользователя',
    tags=['Users'],
)
def get_user() -> UserDetailsResponse:
    return UserDetailsResponse(
        email='example@example.com',
        isActive=True,
        profileId=1,
        registeredAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        updatedAt=datetime.fromisoformat("2025-06-15T18:29:56+00:00"),
        username='klol1k',
    )


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

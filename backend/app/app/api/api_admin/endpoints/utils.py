from typing import Any

from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app import models, schemas
from app.api import deps
from app.utils import send_test_email

router = APIRouter()

@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
async def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    await send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}

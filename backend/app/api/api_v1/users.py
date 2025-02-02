from fastapi import APIRouter, Depends, HTTPException
from services.user_service import UserService
from schemas.user import UserCreateSchema, UserSchema

router = APIRouter(tags=["users"])


@router.post("/", response_model=UserSchema)
async def create_user(
    user_data: UserCreateSchema,
    user_service: UserService = Depends()
):
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


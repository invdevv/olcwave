from remnawave import RemnawaveSDK
from remnawave.exceptions.general import NotFoundError
from remnawave.models import (
    UsersResponseDto, 
    UserResponseDto,
    GetUserByShortUuidResponseDto,
    GetAllConfigProfilesResponseDto,
    CreateInternalSquadRequestDto
)

from config import settings


remnawave = RemnawaveSDK(base_url=settings.RW_API_URL, token=settings.RW_API_TOKEN)


async def isUserValid(short_uuid: int) -> UserResponseDto | None:
    try:
        user: GetUserByShortUuidResponseDto = await remnawave.users.get_user_by_short_uuid(short_uuid)   # pyright: ignore[reportAssignmentType]
        return user
    except NotFoundError:
        return None

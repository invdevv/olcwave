import yaml

from fastapi import HTTPException, status

from olcrtc.service import ContainersService
from profiles.schemas import ProfileSchema
from profiles.repository import ProfileRepository


class ProfilesService:
    def __init__(self, repo: ProfileRepository) -> None:
        self._repo = repo

    @staticmethod
    def validate(config: str) -> str:
        profile_obj: dict = yaml.safe_load(config)

        profile_obj['mode'] = "srv"
        profile_obj.pop("data", None)
        profile_obj.pop('socks', None)
        profile_obj.pop("crypto", None)

        return yaml.safe_dump(profile_obj, sort_keys=False)

    async def add(self, profile: ProfileSchema):
        profile.profile = ProfilesService.validate(profile.profile)

        if not profile.tag:
            raise HTTPException(status_code=400, detail="Tag cannot be empty")

        profile.tag = profile.tag.replace("-", "")
        await self._repo.add_profile(profile.model_dump())

    async def get(self, tag: str) -> ProfileSchema:
        profile = await self._repo.get_profile(tag)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        return ProfileSchema(**profile)

    async def update(self, tag: str, name: str, profile: str) -> None:
        profile = ProfilesService.validate(profile)
        await self._repo.update_profile(
            tag=tag,
            name=name,
            profile=profile,
        )
        await ContainersService.stop_all_by_config_tag(tag)

    async def delete(self, tag: str) -> None:
        await self._repo.delete_profile(tag)
        await ContainersService.remove_all_by_config_tag(tag)

    async def get_all(self) -> list[ProfileSchema]:
        profiles = await self._repo.get_all_profiles()
        return [ProfileSchema(**profile) for profile in profiles]

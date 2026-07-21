import yaml

from olcrtc.sdk import OlcRTC
from database import async_session_factory
from profiles.db import ProfilesDB
from profiles.schemas import ProfileSchema

class Profiles:
    @staticmethod
    def validate(config: str):
        yaml.safe_load(config)

    @staticmethod
    async def add(profile: ProfileSchema):
        Profiles.validate(profile.profile)

        async with async_session_factory() as db:  
            _= await ProfilesDB.add(db, profile) 

    @staticmethod
    async def get(tag: str):
        async with async_session_factory() as db:
            profile = await ProfilesDB.get(db, tag) 
        return profile

    @staticmethod
    async def update(tag: str, name: str, profile: str):
        async with async_session_factory() as db:  
            _= await ProfilesDB.update(db, tag, name, profile) 

        for cont in OlcRTC.all():
            if tag in cont.name:  # pyright: ignore[reportOperatorIssue]
                OlcRTC.stop(cont.name)  # pyright: ignore[reportArgumentType]

    @staticmethod
    async def delete(tag: str):
        async with async_session_factory() as db:  
            _=await ProfilesDB.delete(db, tag) 

    @staticmethod
    async def get_all() -> list[ProfileSchema]:
        async with async_session_factory() as db:  
            profiles: list[ProfileSchema] = await ProfilesDB.get_all(db) 
        
        return profiles
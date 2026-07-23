import profile
import yaml

from olcrtc.sdk import OlcRTC
from database import async_session_factory
from profiles.db import ProfilesDB
from profiles.schemas import ProfileSchema

class Profiles:
    @staticmethod
    def validate(config: str):
        profile_obj: dict = yaml.safe_load(config)  

        if profile_obj.get('socks', None):
            profile_obj.pop('socks')
        
        if profile_obj.get('crypto', None) is None or profile_obj["crypto"].get('key', None) is None or profile_obj['crypto']["key"] != "":
            profile_obj["crypto"] = {}
            profile_obj["crypto"]["key"] = ""    

        return yaml.safe_dump(profile_obj, sort_keys=False)

    @staticmethod
    async def add(profile: ProfileSchema):
        profile.profile = Profiles.validate(profile.profile)

        profile.tag = profile.tag.replace("-", "")

        async with async_session_factory() as db:  
            _= await ProfilesDB.add(db, profile) 

    @staticmethod
    async def get(tag: str):
        async with async_session_factory() as db:
            profile = await ProfilesDB.get(db, tag) 
        return profile

    @staticmethod
    async def update(tag: str, name: str, profile: str):
        profile = Profiles.validate(profile)

        async with async_session_factory() as db:  
            _= await ProfilesDB.update(db, tag, name, profile) 

        for cont in OlcRTC.all():
            if tag in cont.name:  # pyright: ignore[reportOperatorIssue]
                OlcRTC.stop(cont.name)  # pyright: ignore[reportArgumentType]

    @staticmethod
    async def delete(tag: str):
        async with async_session_factory() as db:  
            _=await ProfilesDB.delete(db, tag) 

        for cont in OlcRTC.all():
            if tag in cont.name:  # pyright: ignore[reportOperatorIssue]
                OlcRTC.stop(cont.name) # pyright: ignore[reportArgumentType]
                OlcRTC.remove(cont.name)  # pyright: ignore[reportArgumentType]



    @staticmethod
    async def get_all() -> list[ProfileSchema]:
        async with async_session_factory() as db:  
            profiles: list[ProfileSchema] = await ProfilesDB.get_all(db) 
        
        return profiles
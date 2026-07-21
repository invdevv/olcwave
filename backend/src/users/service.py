from datetime import datetime

from database import async_session_factory
from users.db import UserDB
from users.schemas import UserSchema

class Users:
    @staticmethod
    async def add(user: UserSchema):
        async with async_session_factory() as db:  
            _= await UserDB.add(db, user) 

    @staticmethod
    async def get(short_uuid: str):
        async with async_session_factory() as db:
            user = await UserDB.get(db, short_uuid) 
        return user

    @staticmethod
    async def update(short_uuid: str, expires_at: datetime):
        async with async_session_factory() as db:  
            _= await UserDB.update(db, short_uuid, expires_at) 

    @staticmethod
    async def delete(short_uuid: str):
        async with async_session_factory() as db:  
            _=await UserDB.delete(db, short_uuid) 

        
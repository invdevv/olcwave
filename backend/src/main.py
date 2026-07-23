import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from auth.router import router as auth_router
from settings.service import SettingsService
from profiles.router import router as configs_router
from users.router import router as users_router
from subscriptions.router import router as subscriptions_router
from olcrtc.router import router as containers_router
from config import settings
from database import create_tables
from traffic import TrafficManager


async def lifespan(app: FastAPI):
    await create_tables() # TODO: add alembic migrations
    await SettingsService.load()

    task = asyncio.create_task(TrafficManager.run())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)  # pyright: ignore[reportArgumentType]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(configs_router)
app.include_router(users_router)
app.include_router(subscriptions_router)
app.include_router(containers_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")

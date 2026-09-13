# Copyright (C) 2026 invdevv - https://github.com/invdevv
# This file is part of olcwave.
# OLCWave is free software licensed under AGPL-3.0.

import asyncio
from contextlib import asynccontextmanager
from typing import Literal

import uvicorn
from aiodocker import DockerError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routing.service import RoutingService
from settings.service import SettingsService
from settings.router import router as settings_router
from auth.router import router as auth_router
from profiles.router import router as configs_router
from users.router import router as users_router
from subscriptions.router import router as subscriptions_router
from olcrtc.router import router as containers_router
from routing.router import router as routing_router
from rw_sync import SyncManager
from core.config import settings
from core.factories import (
    get_sync_manager,
    get_settings_service,
    get_traffic_manager,
    get_routing_service,
    get_xray_core_client,
)
from db.base import create_tables
from traffic import TrafficManager
from docker_client import docker_client


@asynccontextmanager
async def lifespan(
    app: FastAPI,
    routing_service: RoutingService = get_routing_service(),
    settings_service: SettingsService = get_settings_service(),
    traffic_manager: TrafficManager = get_traffic_manager(),
    sync_manager: SyncManager = get_sync_manager(),
):
    await create_tables()
    docker = docker_client.client
    xraycore = get_xray_core_client()
    await settings_service.load()

    try:
        routing = await routing_service.get()
    except HTTPException:
        routing = False

    if routing:
        await xraycore.run(routing)

    if settings.RW_ENABLED:
        sync_manager.start()

    traffic_task = asyncio.create_task(traffic_manager.run())

    yield

    traffic_task.cancel()
    try:
        await traffic_task
    except asyncio.CancelledError:
        pass

    if settings.RW_ENABLED:
        await sync_manager.stop()

    try:
        await xraycore.stop()
    except DockerError:
        pass
    await docker.close()


app = FastAPI(
    lifespan=lifespan,
    openapi_url="",
    docs_url="",
    redoc_url=""
)

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
app.include_router(settings_router)
app.include_router(routing_router)


@app.get("/health")
async def healthcheck() -> Literal['ok']:
    return "ok"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")

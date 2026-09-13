from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status

from auth.dependencies import get_current_admin
from xraycore.sdk import XrayCoreClient
from olcrtc.schemas import (
    ContainerSchema,
    ContainerConfigSchema,
    ContainerLogsSchema,
    ContainerStatsSchema,
)
from olcrtc.service import ContainersService
from core.factories import get_users_service, get_xray_core_client
from users.service import UsersService


router = APIRouter(prefix="/containers", tags=["containers"])


@router.get("/all")
async def get_all(
    _admin: dict = Depends(get_current_admin)
) -> list[ContainerSchema]:
    return await ContainersService.all()


@router.post("/run")
async def run(
    name: str,
    _admin: dict = Depends(get_current_admin),
    users_service: UsersService = Depends(get_users_service)
):
    # Block starting a container when its owner has exceeded their traffic limit.
    parts = name.split("-", 2)
    if len(parts) == 3 and parts[0] == "olcwave":
        try:
            traffic = await users_service.get_traffic(parts[2])
        except Exception:
            traffic = None
        if traffic and traffic.exceeded:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="traffic_limit_exceeded",
            )

    await ContainersService.start(name)

    return "ok"


@router.post("/stop")
async def stop(name: str, _admin: dict = Depends(get_current_admin)):
    await ContainersService.stop(name)

    return "ok"


@router.post("/restart")
async def restart(
    name: str,
    _admin: dict = Depends(get_current_admin),
    xray_core_client: XrayCoreClient = Depends(get_xray_core_client),
) -> Literal['ok']:
    if await xray_core_client.is_running():
        await ContainersService.restart(name, "host.docker.internal:10808")
    else:
        await ContainersService.restart(name)
    return "ok"


@router.delete("/")
async def remove(
    name: str,
    _admin: dict = Depends(get_current_admin)
) -> Literal['ok']:
    await ContainersService.remove(name)

    return "ok"


@router.get("/logs")
async def logs(
    name: str,
    _admin: dict = Depends(get_current_admin)
) -> ContainerLogsSchema:
    return await ContainersService.logs(name)


@router.get("/config")
async def get_config(
    name: str,
    _admin: dict = Depends(get_current_admin)
) -> ContainerConfigSchema:
    return await ContainersService.get_config(name)


@router.get("/stats")
async def get_stats(
    name: str,
    _admin: dict = Depends(get_current_admin)
) -> ContainerStatsSchema:
    return await ContainersService.get_stats(name)

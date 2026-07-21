from fastapi import APIRouter, Depends

from auth.dependencies import get_current_admin
from olcrtc.schemas import ContainerSchema, ContainerConfigSchema, ContainerLogsSchema
from olcrtc.service import Containers

router = APIRouter(prefix="/containers", tags=["containers"])

@router.get("/all")
async def get_all(_admin: dict = Depends(get_current_admin)) -> list[ContainerSchema]:
    return Containers.all()

@router.post("/run")
async def run(name: str, _admin: dict = Depends(get_current_admin)):
    Containers.run(name)

    return "ok"

@router.post("/stop")
async def stop(name: str, _admin: dict = Depends(get_current_admin)):
    Containers.stop(name)

    return "ok"

@router.post("/restart")
async def restart(name: str, _admin: dict = Depends(get_current_admin)):
    Containers.restart(name)

    return "ok"

@router.delete("/")
async def remove(name: str, _admin: dict = Depends(get_current_admin)):
    Containers.remove(name)

    return "ok"

@router.get("/logs")
async def logs(name: str, _admin: dict = Depends(get_current_admin)) -> ContainerLogsSchema:
    return Containers.logs(name)

@router.get("/config")
async def get_config(name: str, _admin: dict = Depends(get_current_admin)) -> ContainerConfigSchema:
    return Containers.get_config(name)

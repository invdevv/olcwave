from typing import Literal

from fastapi import APIRouter, Depends, Body, HTTPException

from auth.dependencies import get_current_admin
from xraycore.sdk import XrayCoreClient
from routing.service import RoutingService
from core.factories import get_routing_service, get_xray_core_client

router = APIRouter(prefix="/routing", tags=["routing"])


@router.get("/enabled")
async def check_enabled(
    _admin: dict = Depends(get_current_admin),
    routing_service: RoutingService = Depends(get_routing_service),
) -> bool:
    try:
        # if enabled -> record in db exists -> True; if not error 404
        await routing_service.get()
    except HTTPException:
        return False
    return True


@router.get("/config")
async def get(
    _admin: dict = Depends(get_current_admin),
    routing_service: RoutingService = Depends(get_routing_service),
) -> str:
    return await routing_service.get()


@router.post("/config")
async def create(
    xray_json: str = Body(),
    _admin: dict = Depends(get_current_admin),
    routing_service: RoutingService = Depends(get_routing_service),
) -> Literal['ok']:
    await routing_service.create(xray_json)

    return "ok"


@router.put("/config")
async def update(
    xray_json: str = Body(),
    _admin: dict = Depends(get_current_admin),
    routing_service: RoutingService = Depends(get_routing_service),
):
    await routing_service.update(xray_json)


@router.delete("/config")
async def delete(
    _admin: dict = Depends(get_current_admin),
    routing_service: RoutingService = Depends(get_routing_service),
):
    await routing_service.delete()


@router.get("/logs")
async def logs(
    _admin: dict = Depends(get_current_admin),
    xray_core_client: XrayCoreClient = Depends(get_xray_core_client),
) -> str:
    return await xray_core_client.logs()


@router.get("/geotags")
async def get_geotags(
    _admin: dict = Depends(get_current_admin),
    routing_service: RoutingService = Depends(get_routing_service),
) -> dict[str, list[str]]:
    return await routing_service.get_geotags()

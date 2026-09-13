import asyncio
import json

from aiodocker import DockerError
from fastapi import HTTPException, status

from routing.repository import RoutingRepository
from xraycore.sdk import XrayCore
from xraycore.geodata.geodat_pb2 import GeoSiteList, GeoIPList


class RoutingService:
    def __init__(self, repo: RoutingRepository) -> None:
        self._repo = repo

    async def validate_routing_geotags(self, routing: str):
        try:
            geotags = await self.get_geotags()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Cannot load geotags",
            )

        geoip_set = {
            x.lower()
            for x in geotags.get("geoip", [])
        }

        geosite_set = {
            x.lower()
            for x in geotags.get("geosite", [])
        }

        try:
            config = json.loads(routing)
        except (json.JSONDecodeError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid json",
            )

        rules = config.get("routing", {}).get("rules", [])

        if not isinstance(rules, list):
            raise HTTPException(
                status_code=400,
                detail="Routing.rules is required",
            )

        invalid = []

        for rule in rules:
            if not isinstance(rule, dict):
                continue

            for ip_val in rule.get("ip", []):
                if (
                    isinstance(ip_val, str)
                    and ip_val.lower().startswith("geoip:")
                ):
                    code = ip_val[6:].lower()

                    if code not in geoip_set:
                        invalid.append(
                            {
                                "field": "routing.geoip",
                                "value": ip_val,
                                "reason": (
                                    f'"{ip_val}" does not exist '
                                    "in available geoip tags"
                                ),
                            }
                        )

            for domain_val in rule.get("domain", []):
                if (
                    isinstance(domain_val, str)
                    and domain_val.lower().startswith("geosite:")
                ):
                    code = domain_val[8:].lower()

                    if code not in geosite_set:
                        invalid.append(
                            {
                                "field": "routing.geosite",
                                "value": domain_val,
                                "reason": (
                                    f'"{domain_val}" does not exist '
                                    "in available geosite tags"
                                ),
                            }
                        )

        if invalid:
            detail = (
                "Invalid geotag references in routing config:\n"
                + "\n".join(
                    (
                        f'- {e["field"]}: {e["value"]} '
                        f'- {e["reason"]}'
                    )
                    for e in invalid
                )
            )

            raise HTTPException(
                status_code=422,
                detail=detail,
            )

    @staticmethod
    def routing_to_xray_json(routing: str) -> str:
        xray_config = json.loads(routing)

        xray_config["dns"] = {
            "servers": [
                {
                    "address": "1.1.1.1"
                }
            ],
            "queryStrategy": "IPIfNonMatch",
        }

        xray_config["inbounds"] = [
            {
                "tag": "socks",
                "listen": "0.0.0.0",
                "port": 10808,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True,
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": [
                        "http",
                        "tls",
                        "fakedns",
                    ],
                },
            }
        ]

        return json.dumps(
            xray_config,
            indent=2,
        )

    async def create(self, routing: str):
        await self.validate_routing_geotags(routing)

        xray_json = self.routing_to_xray_json(routing)
        await self._repo.add_routing(xray_json)

        await XrayCore.run(xray_json)

        asyncio.create_task(
            self.restart_all("host.docker.internal:10808")
        )

        return xray_json

    async def get(self) -> str:
        routing = await self._repo.get_routing()
        if not routing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Routing not found",
            )
        return routing.get("xray_json", "")

    async def update(self, routing: str) -> str:
        await self.validate_routing_geotags(routing)

        xray_json = self.routing_to_xray_json(routing)
        await self._repo.update_routing(xray_json)

        await XrayCore.run(xray_json)

        asyncio.create_task(
            self.restart_all("host.docker.internal:10808")
        )

        return xray_json

    async def delete(self) -> None:
        await self._repo.delete_routing()

        try:
            await XrayCore.stop()
        except DockerError:
            pass

        asyncio.create_task(
            self.restart_all()
        )

    @staticmethod
    async def get_geotags():
        geoip_data = await XrayCore.get_geoip()
        geosite_data = await XrayCore.get_geosite()

        geoip = GeoIPList()
        geosite = GeoSiteList()

        geoip.ParseFromString(
            geoip_data
        )

        geosite.ParseFromString(
            geosite_data
        )

        return {
            "geoip": [
                x.code.lower()
                for x in geoip.entry
            ],
            "geosite": [
                x.code.lower()
                for x in geosite.entry
            ],
        }

    @staticmethod
    async def restart_all(upstream_proxy_addr: str = ""):
        from olcrtc.service import Containers

        sem = asyncio.Semaphore(10)

        async def restart_one(container):
            async with sem:
                await Containers.restart(
                    container.name,
                    upstream_proxy_addr=upstream_proxy_addr
                )

        containers = await Containers.all()

        await asyncio.gather(
            *(restart_one(c) for c in containers)
        )

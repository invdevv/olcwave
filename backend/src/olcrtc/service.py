import asyncio

from aiodocker.containers import DockerContainer

from xraycore.sdk import XrayCoreClient
from olcrtc.sdk import OlcRTCClient
from olcrtc.schemas import (
    ContainerConfigSchema,
    ContainerLogsSchema,
    ContainerSchema,
    ContainerStatsSchema,
)


class ContainersService:
    def __init__(
        self,
        xray_core: XrayCoreClient,
        olcrtc_client: OlcRTCClient,
    ) -> None:
        self._xray_core = xray_core
        self._olcrtc_client = olcrtc_client

    @staticmethod
    async def is_panel_container(cont: DockerContainer) -> bool:
        info = await cont.show()

        name = info["Name"].lstrip("/")
        parts = name.split("-", 2)

        return len(parts) == 3 and parts[0] == "olcwave"

    @staticmethod
    async def to_schema(cont: DockerContainer) -> ContainerSchema | None:
        info = await cont.show()

        name = info["Name"].lstrip("/")
        parts = name.split("-", 2)

        if len(parts) != 3:
            return None

        _, config_tag, user_id = parts

        return ContainerSchema(
            id=info["Id"][:12],
            name=name,
            short_uuid=user_id,
            config_tag=config_tag,
            status=info["State"]["Status"],
            created=info["Created"],
            image=info["Config"]["Image"],
        )

    async def get_all_containers(self) -> list[ContainerSchema]:
        containers = await self._olcrtc_client.all(include_stopped=True)
        schemas = await asyncio.gather(
            *(self.to_schema(container) for container in containers)
        )
        return [schema for schema in schemas if schema is not None]

    async def run(
        self,
        config: str,
        config_tag: str,
        short_uuid: str,
    ) -> None:
        routing_socks_addr = ""

        if await self._xray_core.is_running():
            routing_socks_addr = "host.docker.internal:10808"

        await self._olcrtc_client.run(
            config=config,
            config_tag=config_tag,
            user_id=short_uuid,
            upstream_proxy_addr=routing_socks_addr,
        )

    async def start(self, name: str) -> None:
        await self._olcrtc_client.start(name)

    async def stop(self, name: str) -> None:
        await self._olcrtc_client.stop(name)

    async def restart(
        self,
        name: str,
        upstream_proxy_addr: str = "",
        upstream_proxy_user: str = "",
        upstream_proxy_pass: str = "",
    ) -> None:
        await self._olcrtc_client.restart(
            name=name,
            upstream_proxy_addr=upstream_proxy_addr,
            upstream_proxy_user=upstream_proxy_user,
            upstream_proxy_pass=upstream_proxy_pass,
        )

    async def remove(self, name: str) -> None:
        await self._olcrtc_client.remove(name)

    async def logs(self, name: str) -> ContainerLogsSchema:
        logs = await self._olcrtc_client.logs(name)
        return ContainerLogsSchema(
            name=name,
            logs=logs,
        )

    async def get_config(self, name: str) -> ContainerConfigSchema:
        config = await self._olcrtc_client.get_config(name)

        if isinstance(config, bytes):
            config = config.decode()

        return ContainerConfigSchema(
            name=name,
            config=config,
        )

    async def get_stats(self, name: str) -> ContainerStatsSchema:
        data = await self._olcrtc_client.get_stats(name)

        return ContainerStatsSchema(
            name=name,
            upload_bytes=int(data.get("upload_bytes", 0)),
            download_bytes=int(data.get("download_bytes", 0)),
            total_bytes=int(data.get("total_bytes", 0)),
            upload_rate_bps=int(data.get("upload_rate_bps", 0)),
            download_rate_bps=int(data.get("download_rate_bps", 0)),
        )

    async def stop_all_by_short_uuid(self, short_uuid: str) -> None:
        containers = await self.get_all_containers()

        await asyncio.gather(
            *(
                self.stop(container.name)
                for container in containers
                if container.short_uuid == short_uuid
            )
        )

    async def stop_all_by_config_tag(self, config_tag: str) -> None:
        containers = await self.get_all_containers()

        await asyncio.gather(
            *(
                self.stop(container.name)
                for container in containers
                if container.config_tag == config_tag
            )
        )

    async def remove_all_by_short_uuid(self, short_uuid: str) -> None:
        containers = await self.get_all_containers()

        await asyncio.gather(
            *(
                self.remove(container.name)
                for container in containers
                if container.short_uuid == short_uuid
            )
        )

    async def remove_all_by_config_tag(self, config_tag: str) -> None:
        containers = await self.get_all_containers()

        await asyncio.gather(
            *(
                self.remove(container.name)
                for container in containers
                if container.config_tag == config_tag
            )
        )

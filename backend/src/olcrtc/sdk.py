import json
from functools import lru_cache

import yaml
from aiodocker import Docker, DockerError
from aiodocker.containers import DockerContainer

from docker_client import docker_client, DockerClient


class OlcRTCClient:
    def __init__(self, docker_client: DockerClient) -> None:
        self._docker_client = docker_client

    @property
    def _docker(self) -> Docker:
        return self._docker_client.client

    async def build(self, rebuild: bool = False) -> None:
        if not rebuild:
            try:
                _ = await self._docker.images.get("olcrtc")
                return
            except DockerError:
                pass

        _ = await self._docker.images.build(
            path_dockerfile="olcrtc",
            tag="olcrtc",
            rm=True,
            forcerm=True
        )

    async def run(
        self,
        config: str,
        config_tag: str,
        user_id: str,
        upstream_proxy_addr: str = "",
        upstream_proxy_user: str = "",
        upstream_proxy_pass: str = ""
    ) -> DockerContainer:
        name = f"olcwave-{config_tag}-{user_id}"

        try:
            old = await self._docker.containers.get(name)
            await old.delete(force=True)
        except DockerError:
            pass

        container = await self._docker.containers.create(
            config={
                "Image": "olcrtc",
                "Env": [
                    f"CONFIG={config}",
                    f"UPSTREAM_SOCKS={upstream_proxy_addr}",
                    f"UPSTREAM_USER={upstream_proxy_user}",
                    f"UPSTREAM_PASS={upstream_proxy_pass}",
                ],
                "HostConfig": {
                    "ExtraHosts": [
                        "host.docker.internal:host-gateway",
                    ]
                },
            },
            name=name,
        )

        await container.start()

        return container

    async def start(self, name: str) -> None:
        container = await self._docker.containers.get(name)
        await container.start()

    async def stop(self, name: str) -> None:
        container = await self._docker.containers.get(name)
        await container.stop()

    async def restart(
        self,
        name: str,
        upstream_proxy_addr: str = "",
        upstream_proxy_user: str = "",
        upstream_proxy_pass: str = "",
    ) -> None:
        container = await self._docker.containers.get(name)

        info = await container.show()

        image = info["Config"]["Image"]

        env = {}
        for item in info["Config"].get("Env", []):
            if "=" in item:
                k, v = item.split("=", 1)
                env[k] = v

        env["UPSTREAM_SOCKS"] = upstream_proxy_addr
        env["UPSTREAM_USER"] = upstream_proxy_user
        env["UPSTREAM_PASS"] = upstream_proxy_pass

        if "CONFIG" in env:
            try:
                cfg = yaml.safe_load(env["CONFIG"])
                if isinstance(cfg, dict):
                    cfg.pop("data", None)
                    env["CONFIG"] = yaml.dump(cfg)
            except yaml.YAMLError:
                pass

        state = info["State"]["Status"]

        if state == "running":
            await container.delete(force=True)

        new_container = await self._docker.containers.create(
            config={
                "Image": image,
                "Env": [f"{k}={v}" for k, v in env.items()],
                "HostConfig": {
                    "ExtraHosts": [
                        "host.docker.internal:host-gateway",
                    ]
                },
            },
            name=name,
        )

        await new_container.start()

    async def logs(self, name: str) -> str:
        container = await self._docker.containers.get(name)
        logs = await container.log(stdout=True, stderr=True)
        return "".join(logs)

    async def remove(self, name: str) -> None:
        container = await self._docker.containers.get(name)
        await container.delete(force=True)

    async def get(self, name: str) -> DockerContainer:
        return await self._docker.containers.get(name)

    async def all(self, include_stopped: bool = False) -> list[DockerContainer]:
        return await self._docker.containers.list(all=include_stopped)

    async def get_config(self, name: str) -> str:
        container = await self._docker.containers.get(name)

        exec_ = await container.exec(cmd=["cat", "/tmp/olcwave/config.yaml"])
        stream = exec_.start(detach=False)
        config = await stream.read_out()
        if not config:
            return ""
        return config.data.decode().strip()

    async def get_stats(self, name: str) -> dict:
        container = await self._docker.containers.get(name)

        exec_ = await container.exec(
            cmd=["cat", "/tmp/olcwave/stats.json"]
        )
        stream = exec_.start(detach=False)
        result = await stream.read_out()
        if not result:
            return {}

        raw = result.data.decode().strip()

        if not raw:
            return {}

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}

        return data if isinstance(data, dict) else {}


@lru_cache
def get_olcrtc_client() -> OlcRTCClient:
    return OlcRTCClient(docker_client)


OlcRTC = get_olcrtc_client()

from functools import lru_cache

from aiodocker import Docker


class DockerClient:
    def __init__(self, docker: Docker | None = None) -> None:
        self._docker = docker

    @property
    def client(self) -> Docker:
        # aiodocker creates an aiohttp connector and therefore must be
        # instantiated while an asyncio event loop is running.  Keep this
        # singleton import-safe and initialize the actual client on first use.
        if self._docker is None:
            self._docker = Docker()
        return self._docker

    async def close(self) -> None:
        if self._docker is not None:
            await self._docker.close()
            self._docker = None


@lru_cache
def get_docker_client() -> DockerClient:
    return DockerClient()


docker_client = get_docker_client()

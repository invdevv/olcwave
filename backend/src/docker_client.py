from functools import lru_cache

from aiodocker import Docker


class DockerClient:
    def __init__(self, docker: Docker) -> None:
        self._docker = docker

    @property
    def client(self) -> Docker:
        return self._docker

    async def close(self) -> None:
        await self._docker.close()


@lru_cache
def get_docker_client() -> DockerClient:
    return DockerClient(Docker())


docker_client = get_docker_client()

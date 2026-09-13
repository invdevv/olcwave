import io
import tarfile

from aiodocker import Docker, DockerError
from aiodocker.containers import DockerContainer
from utils.docker_client import DockerClient


class XrayCoreClient:
    CONTAINER_NAME = "olcwave-xraycore"

    def __init__(self, docker_client: DockerClient) -> None:
        self._docker_client = docker_client

    @property
    def _docker(self) -> Docker:
        return self._docker_client.client

    async def run(self, xray_json: str) -> DockerContainer:
        try:
            old = await self._docker.containers.get(self.CONTAINER_NAME)
            await old.delete(force=True)
        except DockerError:
            pass

        container = await self._docker.containers.create(
            config={
                "Image": "xraycore",
                "Env": [
                    f"CONFIG={xray_json}",
                ],
                "HostConfig": {
                    "PortBindings": {
                        "10808/tcp": [
                            {
                                "HostIp": "172.17.0.1",
                                "HostPort": "10808",
                            }
                        ],
                        "10808/udp": [
                            {
                                "HostIp": "172.17.0.1",
                                "HostPort": "10808",
                            }
                        ],
                    },
                },
                "ExposedPorts": {
                    "10808/tcp": {},
                    "10808/udp": {},
                },
            },
            name=self.CONTAINER_NAME,
        )

        await container.start()

        return container

    async def start(self) -> None:
        try:
            container = await self._docker.containers.get(self.CONTAINER_NAME)
            await container.start()
        except DockerError:
            print("XRAY CONTAINER NOT FOUND")

    async def stop(self) -> None:
        container = await self._docker.containers.get(self.CONTAINER_NAME)
        await container.stop()

    async def logs(self) -> str:
        container = await self._docker.containers.get(self.CONTAINER_NAME)
        logs = await container.log(stdout=True, stderr=True)
        return "".join(logs)

    async def get(self) -> DockerContainer:
        return await self._docker.containers.get(self.CONTAINER_NAME)

    async def is_running(self) -> bool:
        try:
            container = await self._docker.containers.get(self.CONTAINER_NAME)
            info = await container.show()
            return info["State"]["Status"] == "running"
        except DockerError:
            return False

    async def _get_archive(self, path: str) -> bytes:
        async with self._docker._query(
            f"containers/{self.CONTAINER_NAME}/archive",
            method="GET",
            params={"path": path},
        ) as response:
            archive = await response.read()

            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:*") as tar:
                member = tar.getmembers()[0]

                fp = tar.extractfile(member)
                if fp is None:
                    raise FileNotFoundError(path)

                return fp.read()

    async def get_geoip(self) -> bytes:
        return await self._get_archive("/app/geoip.dat")

    async def get_geosite(self) -> bytes:
        return await self._get_archive("/app/geosite.dat")

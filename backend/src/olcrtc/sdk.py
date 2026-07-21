import docker
from docker.errors import ImageNotFound
from docker.models.containers import Container

client = docker.from_env()


class OlcRTC:
    @staticmethod
    def build(rebuild: bool = False):
        if not rebuild:
            try:
                _=client.images.get("olcrtc")
                return
            except ImageNotFound:
                pass

        _=client.images.build(
            path="olcrtc",
            tag="olcrtc",
            rm=True,
            forcerm=True
        )

    @staticmethod
    def run(config: str, config_tag: str, user_id: str, rebuild: bool = False):
        OlcRTC.build(rebuild)

        name = f"olcwave-{config_tag}-{user_id}"

        try:
            old = client.containers.get(name)
            old.remove(force=True)
        except Exception:
            pass

        return client.containers.run(
            image="olcrtc",
            name=name,
            detach=True,
            environment={
                "CONFIG": config,
            }
        )

    @staticmethod
    def stop(name: str):
        client.containers.get(name).stop()

    @staticmethod
    def logs(name: str) -> str:
        return client.containers.get(name).logs().decode()

    @staticmethod
    def all() -> list[Container]:
        return client.containers.list()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    
    @staticmethod
    def get_config(name: str):
        return client.containers.get(name).exec_run("cat /app/config.yaml")  # pyright: ignore[reportUnknownMemberType]
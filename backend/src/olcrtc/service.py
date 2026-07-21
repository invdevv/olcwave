from docker.models.containers import Container

from olcrtc.sdk import OlcRTC
from olcrtc.schemas import ContainerSchema, ContainerConfigSchema, ContainerLogsSchema

class Containers:
    @staticmethod
    def is_panel_container(cont: Container) -> bool:
        parts = cont.name.split("-")  # pyright: ignore[reportOptionalMemberAccess]
        return len(parts) == 3 and parts[0] == "olcwave"

    @staticmethod
    def to_schema(cont: Container) -> ContainerSchema:
        _, config_tag, user_id = cont.name.split("-")  # pyright: ignore[reportOptionalMemberAccess]

        return ContainerSchema(
            id=cont.short_id, 
            name=cont.name,  # pyright: ignore[reportArgumentType]
            user_id=user_id,
            config_tag=config_tag,
            status=cont.status,
            created=cont.attrs.get("Created", ""),  # pyright: ignore[reportAny]
            image=cont.image.tags[0] if cont.image and cont.image.tags else "olcrtc",  # pyright: ignore[reportOptionalMemberAccess]
        )

    @staticmethod
    def all() -> list[ContainerSchema]:
        return [
            Containers.to_schema(cont)
            for cont in OlcRTC.all(include_stopped=True)
            if Containers.is_panel_container(cont)
        ]

    @staticmethod
    def run(name: str):
        OlcRTC.start(name)

    @staticmethod
    def stop(name: str):
        OlcRTC.stop(name)

    @staticmethod
    def restart(name: str):
        OlcRTC.restart(name)

    @staticmethod
    def remove(name: str):
        OlcRTC.remove(name)

    @staticmethod
    def logs(name: str) -> ContainerLogsSchema:
        return ContainerLogsSchema(name=name, logs=OlcRTC.logs(name))

    @staticmethod
    def get_config(name: str) -> ContainerConfigSchema:
        config: str = OlcRTC.get_config(name).output.decode()  # pyright: ignore[reportAny]
        return ContainerConfigSchema(name=name, config=config)

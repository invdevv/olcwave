import asyncio
import secrets
from typing import Any

import emoji
import yaml

from fastapi import Response

from core.config import settings
from olcrtc.sdk import OlcRTCClient
from settings.service import SettingsService
from users.schemas import TrafficInfoSchema, UserSchema
from profiles.roomGenerator import RoomChecker, RoomGenerator
from profiles.service import ContainersService
from profiles.service import ProfilesService
from settings.service import SettingsService
from remnawave.service import RemnawaveService
from users.service import UsersService


TRANSPORT_NAMES = {
    "vp8channel": "vp8",
    "seichannel": "sei",
    "videochannel": "video",
}

TRANSPORT_OPTIONS = {
    "vp8": {
        "fps": "vp8-fps",
        "batch_size": "vp8-batch",
    },
    "sei": {
        "fps": "fps",
        "batch_size": "batch",
        "fragment_size": "frag",
        "ack_timeout_ms": "ack-ms",
    },
    "video": {
        "width": "video-w",
        "height": "video-h",
        "fps": "video-fps",
        "bitrate": "video-bitrate",
        "hw": "video-hw",
        "codec": "video-codec",
        "qr_size": "video-qr-size",
        "qr_recovery": "video-qr-recovery",
        "tile_module": "video-tile-module",
        "tile_rs": "video-tile-rs",
    },
}


def bytes_to_notation(num: float):
    notations = ["b", "kb", "mb", "gb", "tb"]
    ptr = 0
    while num > 1000 and ptr < len(notations) - 1:
        num /= 1000
        ptr += 1

    return f"{int(num)}{notations[ptr]}"


class SubscriptionsService:
    def __init__(
        self,
        remnawave_service: RemnawaveService,
        users_service: UsersService,
        settings_service: SettingsService,
        profiles_service: ProfilesService,
        containers_service: ContainersService,
        olcrtc_client: OlcRTCClient,
    ) -> None:
        self._remnawave_service = remnawave_service
        self._users_service = users_service
        self._settings_service = settings_service
        self._profiles_service = profiles_service
        self._containers_service = containers_service
        self._olcrtc_client = olcrtc_client

    @staticmethod
    def remove_last_emoji(s: str) -> tuple[str, str]:
        matches = list(emoji.emoji_list(s))
        if not matches:
            return s, ""

        last = matches[-1]

        return (
            s[:last["match_start"]] + s[last["match_end"]:],
            last["emoji"],
        )

    @staticmethod
    async def profile_to_config(profile: str):
        config = yaml.safe_load(profile)
        config.pop("data", None)
        config.setdefault("crypto", {})["key"] = secrets.token_hex(32)
        if (
            config["auth"]["provider"] in ["telemost", "wbstream"]
            and config["auth"].get("token", "") != ""
            and config.get("room", {}).get("id", "") == ""
        ):
            room_id = await RoomGenerator.generate_room_id(
                config["auth"]["provider"],
                config["auth"]["token"],
            )

            if not room_id:
                raise RuntimeError(
                    "Failed to generate room id"
                )

            config["room"] = config.get("room", {})
            config["room"]["id"] = room_id

        if config["auth"]["provider"] == "telemost":
            config["auth"].pop("token", None)

        if config["auth"]["provider"] == "jitsi":
            room_url = config["room"]["id"].split("/")

            if len(room_url) == 3:
                room_url.append(
                    str(secrets.token_hex(16))
                )

            elif len(room_url) == 4 and not room_url[3]:
                room_url[3] = str(secrets.token_hex(16))

            config["room"]["id"] = "/".join(room_url)
        return yaml.dump(config)

    @staticmethod
    def build_transport_options(cfg: dict) -> str:
        transport = cfg["net"]["transport"]

        if transport == "datachannel":
            return ""

        short = TRANSPORT_NAMES[transport]

        params = "&".join(
            f"{TRANSPORT_OPTIONS[short][k]}={v}"
            for k, v in cfg[short].items()
        )

        return f"<{params}>"

    @staticmethod
    def config_to_uri(config: str, name: str) -> str:
        cfg = yaml.safe_load(config)

        options = SubscriptionsService.build_transport_options(cfg)

        return (
            f"olcrtc://{cfg['auth']['provider']}?"
            f"{cfg['net']['transport']}"
            f"{options}"
            f"@{cfg['room']['id']}#"
            f"{cfg['crypto']['key']}${name}"
        )

    async def get_launched_tags(self, short_uuid: str):
        servers = []

        for srv in await self._olcrtc_client.all():
            if await ContainersService.is_panel_container(srv):
                info = await srv.show()
                name = info["Name"].lstrip("/")

                if name.endswith(short_uuid):
                    servers.append(
                        name.split("-", 2)[1]
                    )

        return servers

    def prepare_sub_text(
        self,
        uris: list[str],
        name: str,
        used: int = 0,
        limit: int = 0,
    ):
        txt = (
            f"#name: {name}\n"
            f"#update: 2147483647\n"
            f"#refresh: {self._settings_service.get().sub_update_interval}\n"
        )
        if limit == 0:
            txt += f"#used: {bytes_to_notation(used)}\n"
        else:
            txt += (
                f"#used: {bytes_to_notation(used)}/"
                f"{bytes_to_notation(limit)}\n"
                f"#available: "
                f"{bytes_to_notation(limit-used)}\n\n"
            )

        for uri in uris:
            name = uri[uri.find("$") + 1:]

            name, icon = SubscriptionsService.remove_last_emoji(name)

            txt += (
                f"{uri}\n"
                f"##name: {name}\n"
            )

            if icon:
                txt += f"##icon: {icon}"

        return txt

    async def _cleanup_user_containers(self, short_uuid: str):
        for container in await self._olcrtc_client.all(True):
            info = await container.show()
            name = info["Name"].lstrip("/")

            if (
                name.startswith("olcwave-")
                and name.endswith(f"-{short_uuid}")
            ):
                await self._olcrtc_client.remove(name)

    async def _validate_rw_user(self, short_uuid: str) -> Any | None:
        rw_user = await self._remnawave_service.get_subscription_info(short_uuid)
        if rw_user:
            return rw_user
        return None

    async def _ensure_local_user_from_rw(
        self,
        short_uuid: str,
        rw_user: Any
    ) -> None:
        try:
            await self._users_service.get(short_uuid)
        except Exception:
            await self._users_service.add(
                UserSchema(
                    short_uuid=short_uuid,
                    name=rw_user.user.username,
                    expires_at=rw_user.user.expires_at,
                )
            )

    def traffic_limit_response(self, traffic: TrafficInfoSchema):
        traffic_uri = (
            "olcrtc://wbstream?"
            "datachannel@0#"
            "0000000000000000000000000000000000000000000000000000000000000000"
            "$Traffic limit exceeded"
        )

        return Response(
            content=self.prepare_sub_text(
                [traffic_uri],
                self._settings_service.get().sub_name,
                traffic.used,
                traffic.limit,
            ),
            status_code=403,
            media_type="text/plain",
        )

    async def ensure_profiles_running(self, short_uuid: str):

        running_tags = await self.get_launched_tags(short_uuid)

        async def load_config(tag):

            container_name = f"olcwave-{tag}-{short_uuid}"
            config = await self._olcrtc_client.get_config(
                container_name
            )

            if isinstance(config, bytes):
                config = config.decode()
            return tag, config

        loaded = await asyncio.gather(
            *(load_config(tag) for tag in running_tags)
        )

        configs = dict(loaded)

        async def check_profile(tag, config):

            obj = yaml.safe_load(config)

            provider = obj["auth"]["provider"]

            if provider in ("telemost", "wbstream"):

                exists = await RoomChecker.check_room_id(
                    provider,
                    obj["room"]["id"],
                    obj["auth"].get("token", ""),
                )

                if not exists:
                    await self._olcrtc_client.remove(
                        f"olcwave-{tag}-{short_uuid}"
                    )

        await asyncio.gather(
            *(check_profile(tag, cfg)
              for tag, cfg in configs.items())
        )

        profiles_list = await self._profiles_service.get_all()

        profiles = {
            profile.tag: profile
            for profile in profiles_list
        }

        missing = profiles.keys() - configs.keys()

        async def start_profile(tag):
            config = await SubscriptionsService.profile_to_config(
                profiles[tag].profile
            )

            configs[tag] = config

            await self._containers_service.run(
                config,
                tag,
                short_uuid,
            )

        await asyncio.gather(
            *(start_profile(tag) for tag in missing)
        )

        return configs, profiles

    async def get(self, short_uuid: str):
        if settings.RW_ENABLED:
            rw_user = await self._validate_rw_user(short_uuid)
            if rw_user is None:
                await self._cleanup_user_containers(short_uuid)
                return Response(status_code=404)

            await self._ensure_local_user_from_rw(short_uuid, rw_user)
        else:
            try:
                await self._users_service.get(short_uuid)
            except Exception:
                return Response(status_code=404)

        traffic = await self._users_service.get_traffic(short_uuid)
        if traffic.exceeded:
            return self.traffic_limit_response(
                traffic
            )

        configs, profiles = await self.ensure_profiles_running(
            short_uuid
        )

        uris = [
            self.config_to_uri(
                configs[tag],
                profiles[tag].name,
            )
            for tag in profiles
        ]

        return Response(
            content=self.prepare_sub_text(
                uris,
                self._settings_service.get().sub_name,
                traffic.used,
                traffic.limit,
            ),
            media_type="text/plain",
        )

from fastapi import Response
from remnawave.models import SubscriptionInfoResponseDto

from settings.service import SettingsService
from users.schemas import TrafficInfoSchema, UserSchema
from olcrtc.sdk import OlcRTC
from profiles.roomGenerator import RoomChecker, RoomGenerator
from profiles.service import Containers
from profiles.service import Profiles
from rw.sdk import isUserValid
from users.service import Users

import yaml
import random
import emoji

TRANSPORT_NAMES = {
            "vp8channel": "vp8",
            "seichannel": "sei",
            "videochannel": "video"
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


class Subscriptions:
    @staticmethod
    def remove_last_emoji(s: str) -> tuple[str, str]:
        matches = list(emoji.emoji_list(s))
        if not matches:
            return s, ""

        last = matches[-1]
        emoji_value = last["emoji"]

        return s[:last["match_start"]] + s[last["match_end"]:], emoji_value



    @staticmethod
    async def profile_to_config(profile: str):
        config = yaml.safe_load(profile)  # pyright: ignore[reportAny]
        config["crypto"]["key"] = random.randbytes(32).hex()

        if (
            config["auth"]["provider"] in ["telemost", "wbstream"] and
            config["auth"].get("token", "") != "" and
                (
                    config.get("room", {}).get("id", "") == ""
                )
            ):
            generated_room_id = await RoomGenerator.generate_room_id(config["auth"]["provider"], config["auth"]["token"])

            if not generated_room_id:
                raise RuntimeError("Failed to generate room id")

            config["room"] = config.get("room", {})
            config["room"]["id"] = generated_room_id

        if config["auth"]["provider"] == "telemost":
            config["auth"].pop("token")

        if config["auth"]["provider"] == "jitsi":
            roomUrl: list[str] = config["room"]["id"].split("/")  # pyright: ignore[reportAny]

            if len(roomUrl) == 3:
                roomUrl.append(str(random.randbytes(16).hex()))
            elif len(roomUrl) == 4 and not roomUrl[3]:
                roomUrl[3] = str(random.randbytes(16).hex())
            
            config['room']['id'] = "/".join(roomUrl)

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
        cfg = yaml.safe_load(config)  # pyright: ignore[reportAny]

        options = Subscriptions.build_transport_options(cfg)

        return (
            f"olcrtc://{cfg['auth']['provider']}?"
            f"{cfg['net']['transport']}"
            f"{options}"
            f"@{cfg['room']['id']}#"
            f"{cfg['crypto']['key']}${name}"
        )

    @staticmethod
    def get_launched_tags(short_uuid: str):
        servers: list[str] = []
        
        for srv in OlcRTC.all():
            if Containers.is_panel_container(srv) and srv.name.endswith(short_uuid): # pyright: ignore[reportOptionalMemberAccess]
                servers.append(srv.name.split("-")[1])  # pyright: ignore[reportOptionalMemberAccess]

        return servers
    
    @staticmethod
    def prepare_sub_text(uris: list[str], name: str, used: int = 0, limit: int = 0):
        txt = (
            f"#name: {name}\n" \
            f"#update: 2147483647\n" \
            f"#refresh: {SettingsService.get().sub_update_interval}\n"
        )
        if limit == 0:
            txt += f"#used: {bytes_to_notation(used)}\n"
        else:
            txt += (
                f"#used: {bytes_to_notation(used)}/{bytes_to_notation(limit)}\n" \
                f"#available: {bytes_to_notation(limit - used)}\n\n" 
            )

        for uri in uris:
            name = uri[uri.find("$")+1:]
            name, icon = Subscriptions.remove_last_emoji(name)

            txt += f"{uri}\n##name: {name}\n"
            if icon != "":
                txt += f"##icon: {icon}"

        return txt

    @staticmethod
    async def validate_user(short_uuid: str):
        rw_user = await isUserValid(short_uuid)
        if rw_user:
            return rw_user

        for container in OlcRTC.all(include_stopped=True):
            if (
                container.name.startswith("olcwave-")
                and container.name.endswith(f"-{short_uuid}")  # pyright: ignore[reportOperatorIssue]
            ):
                OlcRTC.remove(container.name)  # pyright: ignore[reportArgumentType]

        return Response(status_code=404)

    @staticmethod
    async def ensure_user_exists(short_uuid: str, rw_user: SubscriptionInfoResponseDto):
        try:
            await Users.get(short_uuid)
        except Exception:
            await Users.add(
                UserSchema(
                    short_uuid=short_uuid,
                    name=rw_user.user.username,
                    expires_at=rw_user.user.expires_at,
                )
            )
    
    @staticmethod
    def traffic_limit_response(traffic: TrafficInfoSchema):
        traffic_uri = (
            "olcrtc://wbstream?"
            "datachannel@0#"
            "0000000000000000000000000000000000000000000000000000000000000000"
            "$Traffic limit exceeded"
        )

        return Response(
            content=Subscriptions.prepare_sub_text(
                [traffic_uri],
                SettingsService.get().sub_name,
                traffic.used,
                traffic.limit,
            ),
            status_code=403,
            media_type="text/plain"
        )
    
    @staticmethod
    async def ensure_profiles_running(short_uuid: str):
        running_tags = Subscriptions.get_launched_tags(short_uuid)

        configs = {
            tag: OlcRTC.get_config(f"olcwave-{tag}-{short_uuid}").output.decode()
            for tag in running_tags
        }

        for tag, config in configs.items():
            # get_config() читает /tmp/olcwave/config.yaml из контейнера — это YAML,
            # не JSON. json.loads падал на каждом повторном запросе подписки
            # (когда контейнеры уже существуют), первый запрос всегда маскировал баг.
            config_json = yaml.safe_load(config)
            if config_json["auth"]["provider"] in ("telemost", "wbstream"):
                room_exists = await RoomChecker.check_room_id(
                    config_json["auth"]["provider"],
                    config_json["room"]["id"],
                    config_json["auth"].get("token", ""),
                )

                if not room_exists:
                    container_name = f"olcwave-{tag}-{short_uuid}"
                    OlcRTC.remove(container_name)

        profiles = {
            profile.tag: profile
            for profile in await Profiles.get_all()
        }

        for tag in profiles.keys() - configs.keys():
            config = await Subscriptions.profile_to_config(profiles[tag].profile)
            configs[tag] = config

            Containers.run(config, tag, short_uuid)

        return configs, profiles


    @staticmethod
    async def get(short_uuid: str):
        rw_user = await Subscriptions.validate_user(short_uuid)
        if isinstance(rw_user, Response):
            return rw_user

        await Subscriptions.ensure_user_exists(short_uuid, rw_user)

        traffic = await Users.get_traffic(short_uuid)
        if traffic.exceeded:
            return Subscriptions.traffic_limit_response(traffic)

        configs, profiles = await Subscriptions.ensure_profiles_running(short_uuid)

        uris = [
            Subscriptions.config_to_uri(configs[tag], profiles[tag].name)
            for tag in profiles
        ]

        return Response(
            content=Subscriptions.prepare_sub_text(
                uris,
                SettingsService.get().sub_name,
                traffic.used,
                traffic.limit,
            ),
            media_type="text/plain"
        )
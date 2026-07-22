import base64
import hashlib
import json
from fastapi import Response

from config import settings
from users.schemas import UserSchema
from olcrtc.sdk import OlcRTC
from profiles.service import Profiles
from rw.sdk import isUserValid
from users.service import Users

import yaml
import random
import emoji

class Subscriptions:
    @staticmethod
    def get_last_emoji(s: str) -> str:
        matches = list(emoji.emoji_list(s))
        if not matches:
            return ""

        last = matches[-1]
        return last["emoji"]

    @staticmethod
    def olcrtc_to_olcbox_lbv4(configs: list[str], names: list[str]) -> str: 
        if len(configs) != len(names):
            return "{}"
        locations = []

        for id, conf in enumerate(configs):
            cfg = yaml.safe_load(conf)  # pyright: ignore[reportAny]

            provider = cfg.get("auth", {}).get("provider")  # pyright: ignore[reportAny]

            transport = cfg.get("net", {}).get("transport")  # pyright: ignore[reportAny]

            room = cfg.get("room", {}).get("id", "").strip()  # pyright: ignore[reportAny]
            key = cfg.get("crypto", {}).get("key", "").strip()  # pyright: ignore[reportAny]

            storage_id = hashlib.sha1(conf.encode()).hexdigest()[:16]

            location = {
                "storage_id": storage_id,
                "name": names[id],
                "endpoint": {
                    "room_id": room,
                    "key": key,
                },
                "auth_provider": provider,
                "transport": {
                    "type": transport,
                },
            }

            if transport == "vp8channel":
                vp8 = cfg.get("vp8", {})  # pyright: ignore[reportAny]
                location["transport"]["vp8"] = {  # pyright: ignore[reportIndexIssue]
                    "fps": max(1, min(120, int(vp8.get("fps", 60)))),  # pyright: ignore[reportAny]
                    "batch": max(1, min(64, int(vp8.get("batch", 64)))),  # pyright: ignore[reportAny]
                }

            locations.append(location)  # pyright: ignore[reportUnknownMemberType]

        bundle = {  # pyright: ignore[reportUnknownVariableType]
            "version": 5,
            "active_location_id": locations[0]["storage_id"] if locations else None,
            "locations": locations,
        }

        return json.dumps(bundle, indent=2)

    @staticmethod
    def profile_to_config(profile: str):
        config = yaml.safe_load(profile)  # pyright: ignore[reportAny]
        config["crypto"]["key"] = random.randbytes(32).hex()

        roomUrl: list[str] = config["room"]["id"].split("/")  # pyright: ignore[reportAny]

        if len(roomUrl) == 3:
            roomUrl.append(str(random.randbytes(16).hex()))
        elif len(roomUrl) == 4 and not roomUrl[3]:
            roomUrl[3] = str(random.randbytes(16).hex())
        
        config['room']['id'] = "/".join(roomUrl)

        return yaml.dump(config)

    @staticmethod
    def config_to_uri(config: str, name: str) -> str:
        cfg = yaml.safe_load(config)  # pyright: ignore[reportAny]

        transport_translates = {
            "vp8channel": "vp8",
            "seichannel": "sei",
            "videochannel": "video"
        }
        non_dc_params = {
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

        non_dc_str: str = ""  # pyright: ignore[reportRedeclaration]
        if cfg['net']['transport'] != "datachannel":
            non_dc_str: str = "<"
            transport = transport_translates[cfg['net']['transport']]
            for k, v in cfg[transport].items():  # pyright: ignore[reportAny]
                non_dc_str += f"{non_dc_params[transport][k]}={v}&"
            non_dc_str = non_dc_str[:-1] + ">"

        return (
            f"olcrtc://{cfg['auth']['provider']}?"
            f"{cfg['net']['transport']}"
            f"{non_dc_str}"
            f"@{cfg['room']['id']}#"
            f"{cfg['crypto']['key']}${name}"
        )

    @staticmethod
    def config_to_olcbox_uri(config: str, name: str) -> str:
        # yeah, uris in olcbox are that format
        return f"olcrtc://{base64.b64encode(config.encode()).decode()}${name}"

    @staticmethod
    def get_launched_tags(short_uuid: str):
        servers: list[str] = []
        
        for srv in OlcRTC.all():
            if srv.name.endswith(short_uuid) and len(srv.name.split("-")) == 3 and srv.name.split("-")[0] == "olcwave": # pyright: ignore[reportOptionalMemberAccess]
                servers.append(srv.name.split("-")[1])  # pyright: ignore[reportOptionalMemberAccess]

        return servers
    
    @staticmethod
    def prepare_sub_text(uris: list[str], name: str, used: int = 0, available: int = 0):
        txt = (
            f"#name: {name}\n" \
            f"#update: 2147483647\n" \
            f"#refresh: 1h\n" \
            f"#used: {used}"
            f"#available: {available}"
            "\n" \
        )
        for uri in uris:
            name = uri[uri.find("$")+1:]
            icon = Subscriptions.get_last_emoji(name)

            txt += f"{uri}\n##name: {name}\n"
            if icon != "":
                txt += f"##icon: {icon}"

        return txt


    @staticmethod
    async def get(short_uuid: str): 
        rw_sub = await isUserValid(short_uuid)
        if not rw_sub:
            return Response(status_code=404)
        try:
            _=await Users.get(short_uuid)
        except Exception:
            user = UserSchema(short_uuid=short_uuid, expires_at=rw_sub.user.expires_at)
            await Users.add(user)

        # Block subscription if traffic limit exceeded
        traffic = await Users.get_traffic(short_uuid)
        if traffic.exceeded:
            # string with olcrtc yaml config, for rewrite existing config and say "traffic limit exceeded"
            olcrtc_fake_valid_config = """mode: cnc
auth:
  provider: jitsi
room:
  id: "https://example.org"
crypto:
  key: "0000000000000000000000000000000000000000000000000000000000000000"
net:
  transport: datachannel
  dns: "0.0.0.0:53"
"""

            traffic_uri = (
                f"olcrtc://{base64.b64encode(olcrtc_fake_valid_config.encode()).decode()}"
                "$Traffic limit Exceeded"
            )

            return Response(
                content=Subscriptions.prepare_sub_text(
                    [traffic_uri],
                    settings.NAME,
                    traffic.used,
                    traffic.limit - traffic.used
                ),
                status_code=403,
                media_type="text/plain",
                headers={"profile-update-interval": "1"}
            )

            
        # get configs for servers that already started
        tags = Subscriptions.get_launched_tags(short_uuid)
        configs: dict[str, str] = {tag: OlcRTC.get_config(f"olcwave-{tag}-{short_uuid}").output.decode() for tag in tags}  # pyright: ignore[reportAny]
        
        # get list of all needed configs
        p = await Profiles.get_all()
        profiles = {profile.tag: profile for profile in p}

        # start configs if it already not started
        if set(sorted(tags)) != set(sorted(profiles.keys())):
            missing = set(profiles.keys()) - set(tags)
            for tag in missing:
                config = Subscriptions.profile_to_config(profiles[tag].profile)
                tags.append(tag)
                configs[tag] = config
                _=OlcRTC.run(config, tag, short_uuid)
        
        ordered_tags = list(configs.keys())

        names = [profiles[tag].name for tag in ordered_tags]
        cfgs = [configs[tag] for tag in ordered_tags]

        return Subscriptions.olcrtc_to_olcbox_lbv4(cfgs, names)
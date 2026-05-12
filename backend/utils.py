import subprocess
import shlex

from remnawave.models import SubscriptionInfoResponseDto, SubscriptionSettingsResponseDto


from config import settings


def getSubMD(
        sub: SubscriptionInfoResponseDto,
        subSettings: SubscriptionSettingsResponseDto,
        room_id: str,
        key: str,
        client_id: str
    ):

    subMD = f"""
#name: {subSettings.profile_title}
#update: {2**31 - 1}  
#refresh: {subSettings.profile_update_interval}h

{getOlcRtcUri(room_id, key, client_id)}
##name: {settings.OLCRTC_SERVER_NAME}
"""

def getOlcRtcUri(room_id: str, key: str, client_id: str):
    link = (
        f"olcrtc://"                       \
        f"{settings.OLCRTC_CARRIER}?"      \
        f"{settings.OLCRTC_TRANSPORT}@"    \
        f"{room_id}#"                      \
        f"{key}%"                          \
        f"{client_id}$"                    \
        f"{settings.OLCRTC_SERVER_NAME}"
    )

    return link


def generateCmdParams(room_id: str,  key: str, client_id: str):
    params = (
        f"-carrier {settings.OLCRTC_CARRIER} " \
        f"-transport {settings.OLCRTC_TRANSPORT.split("<", 1)[0]} " \
        f"-id {room_id} " \
        f"-client-id {client_id} " \
        f"-key {key} " \
        f"-link direct " \
        f"-data data " \
    )

    if "<" in settings.OLCRTC_TRANSPORT:
        transport_params = settings.OLCRTC_TRANSPORT[
            settings.OLCRTC_TRANSPORT.find("<")+1 : settings.OLCRTC_TRANSPORT.find(">")
        ].split("&")

        for tp in transport_params:
            tp_key, tp_value = tp.split("=")
            params += f"-{tp_key} {tp_value} "

    return params


def startOlcRtc(*args):
    cmd = [
        "docker", "exec", "-d",
        "olcrtc-container",
        "/app/olcrtc"
    ] + list(args)

    subprocess.Popen(cmd)


def generateRoomID(carrier: str) -> str:
    cmd = [
        "docker", "exec",
        "olcrtc-container",
        "/app/olcrtc",
        "-mode", "gen",
        "-carrier", carrier,
        "-dns", "1.1.1.1:53",
        "-amount", "1"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"olcrtc failed: {result.stderr.strip()}"
        )

    output = result.stdout.strip()

    return output


def getRunningOlcRtc(client_id: str):
    cmd = [
        "docker", "exec",
        "olcrtc-container",
        "ps", "aux"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    for line in result.stdout.splitlines():
        if "/app/olcrtc" not in line:
            continue

        if f"-client-id {client_id}" not in line:
            continue

        args = shlex.split(line)

        key = None
        room_id = None

        for i, arg in enumerate(args):
            if arg == "-key" and i + 1 < len(args):
                key = args[i + 1]

            if arg == "-id" and i + 1 < len(args):
                room_id = args[i + 1]

        return True, key, room_id

    return False, None, None
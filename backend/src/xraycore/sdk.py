import json
import io
import tarfile
import docker
from docker.errors import ImageNotFound, NotFound
from docker.models.containers import Container

client = docker.from_env()


class XrayCore:
    @staticmethod
    def run(xray_json: str):
        name = f"olcwave-xraycore"

        try:
            old = client.containers.get(name)
            old.remove(force=True)
        except Exception:
            pass

        return client.containers.run(
            image="xraycore",
            name="olcwave-xraycore",
            detach=True,
            environment={
                "CONFIG": xray_json,
            },
            # OLCRTC-контейнеры обращаются сюда через upstream_proxy_addr=
            # "host.docker.internal:10808" (см. Routing.restart_all_with_proxy)
            # — на Linux-хостах это резолвится в IP докер-бриджа
            # (обычно 172.17.0.1), а НЕ в 127.0.0.1. При привязке к loopback
            # соединение было физически невозможно (connection refused
            # с любого другого контейнера).
            #
            # Привязывать нужно именно к адресу докер-бриджа, а НЕ к 0.0.0.0—
            # SOCKS5 здесь без авторизации ("auth": "noauth" в
            # routing_to_xray_json), 0.0.0.0 означало бы открытый анонимный
            # прокси наружу в интернет.
            ports={
                "10808/tcp": ("172.17.0.1", 10808),
                "10808/udp": ("172.17.0.1", 10808),
            }
        )

    @staticmethod
    def start():
        try:
            client.containers.get("olcwave-xraycore").start()
        except NotFound:
            print("XRAY CONTAINER NOT FOUND")

    @staticmethod
    def stop():
        client.containers.get("olcwave-xraycore").stop()

    @staticmethod
    def logs() -> str:
        return client.containers.get("olcwave-xraycore").logs().decode()

    @staticmethod
    def get() -> Container:
        return client.containers.get("olcwave-xraycore")

    @staticmethod
    def get_geoip() -> bytes:
        container = client.containers.get("olcwave-xraycore")

        stream, _ = container.get_archive("/app/geoip.dat")

        with tarfile.open(fileobj=io.BytesIO(b"".join(stream))) as tar:
            member = tar.getmembers()[0]
            return tar.extractfile(member).read()

    @staticmethod
    def get_geosite() -> bytes:
        container = client.containers.get("olcwave-xraycore")

        stream, _ = container.get_archive("/app/geosite.dat")

        with tarfile.open(fileobj=io.BytesIO(b"".join(stream))) as tar:
            member = tar.getmembers()[0]
            return tar.extractfile(member).read()
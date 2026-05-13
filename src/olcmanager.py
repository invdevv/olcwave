from remnawave.models import SubscriptionInfoResponseDto

from olcrtc_manager_api.client import OlcrtcManager
from olcrtc_manager_api.models import AddClientRequest, Quota

from config import settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def getOlcManagerApi():
    async with OlcrtcManager(
        settings.OLCRTC_MANAGER_URL,
        settings.OLCRTC_MANAGER_LOGIN,
        settings.OLCRTC_MANAGER_PASSWORD
    ) as api:
        yield api


async def addClient(client_id: str, sub: SubscriptionInfoResponseDto):
    async with getOlcManagerApi() as api:
        quota = Quota(  # pyright: ignore[reportCallIssue]
            expires_at = sub.user.expires_at.strftime("%Y-%m-%d")
        )

        client  = AddClientRequest(
            client_id = client_id,
            carrier = settings.OLCRTC_CARRIER,
            transport = settings.OLCRTC_TRANSPORT,
            name = settings.OLCRTC_SERVER_NAME,
            dns = settings.OLCRTC_DNS,
            quota = quota
        )

        resp = await api.create_client(client)

        return resp


async def getClient(client_id: str):
    async with getOlcManagerApi() as api:
        clients = await api.list_clients()

        client = [client for client in clients if client.client_id == client_id]

        return client[0] if len(client) >= 1 else None


async def getSubscription(client_id: str):
    async with getOlcManagerApi() as api:
        sub = await api.get_subscription(client_id)

        return sub

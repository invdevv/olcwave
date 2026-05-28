from remnawave.models import SubscriptionInfoResponseDto

from olcrtc_manager_api.client import OlcrtcManager
from olcrtc_manager_api.models import AddClientRequest, Location, Quota
from olcrtc_manager_api.utils import getRoomId, getRandomKey

from config import settings

from contextlib import asynccontextmanager

@asynccontextmanager
async def getOlcManagerApi():
    async with OlcrtcManager(
        settings.OLCRTC_MANAGER_URL,
    ) as api:
        await api.login(
            settings.OLCRTC_MANAGER_LOGIN,
            settings.OLCRTC_MANAGER_PASSWORD
        )
        
        yield api


async def addClient(client_id: str, sub: SubscriptionInfoResponseDto):
    async with getOlcManagerApi() as api:
        quota = Quota(  # pyright: ignore[reportCallIssue]
            expires_at = sub.user.expires_at.strftime("%Y-%m-%d")
        )

        location = Location(
            name = settings.OLCRTC_SERVER_NAME,
            room_id = getRoomId(),  # pyright: ignore[reportOptionalOperand, reportArgumentType]
            key = getRandomKey(),
            carrier = settings.OLCRTC_CARRIER,
            transport = settings.OLCRTC_TRANSPORT,  # pyright: ignore[reportArgumentType]
            dns = settings.OLCRTC_DNS,
        )

        client  = AddClientRequest(  # pyright: ignore[reportCallIssue]
            client_id = client_id,
            quota = quota,
            locations=[location]
        )

        resp = await api.add_client(client)

        return resp


async def getClient(client_id: str):
    async with getOlcManagerApi() as api:
        state = await api.get_state()
        clients = state.clients

        client = [client for client in clients if client.client_id == client_id]
        
        return client[0] if len(client) >= 1 else None


async def getSubscription(client_id: str):
    async with getOlcManagerApi() as api:
        sub = await api.get_subscription(settings.OLCRTC_SUB_PATH, client_id)

        return sub

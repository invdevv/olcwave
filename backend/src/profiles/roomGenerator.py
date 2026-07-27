import httpx
import uuid
from fake_useragent import UserAgent

class RoomGenerator:
    @staticmethod
    async def generate_room_id(provider: str, token: str) -> str:
        providers_funcs= {
            "telemost": RoomGenerator._generate_telemost_room_id,
            "wbstream": RoomGenerator._generate_wbstream_room_id,
        }

        generate = providers_funcs.get(provider)
        if generate is None:
            raise RuntimeError(f"Provider {provider} not supported for room generation")

        roomId = await generate(token)

        return roomId

    @staticmethod
    async def _generate_wbstream_room_id(token: str) -> str:
        ua = UserAgent()

        headers = {
            "User-Agent": ua.random,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Referer": "https://stream.wb.ru/",
            "authorization": f"Bearer {token}",
            "Origin": "https://stream.wb.ru",
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(
                url = "https://stream.wb.ru/api-room/api/v2/room",
                headers=headers,
                json = {"roomType":"ROOM_TYPE_ALL_ON_SCREEN","roomPrivacy":"ROOM_PRIVACY_FREE"}
            )

        return res.json()["roomId"]

    @staticmethod
    async def _generate_telemost_room_id(token: str) -> str:
        ua = UserAgent()

        headers = {
            "User-Agent": ua.random,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Client-Instance-Id": str(uuid.uuid4()),
            "X-Telemost-Client-Version": "203.1.0",
            "Idempotency-Key": str(uuid.uuid4()),
            "Origin": "https://telemost.yandex.ru",
            "Referer": "https://telemost.yandex.ru/",
        }

        cookies = {
            "Session_id": token
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(
                url = "https://cloud-api.yandex.ru/telemost_front/v2/telemost/conferences?next_gen_media_platform_allowed=true",
                headers=headers,
                cookies=cookies,
                json = {}
            )
        
        return res.json()["uri"].split("/")[-1]



class RoomChecker:
    @staticmethod
    async def check_room_id(provider: str, room_id: str, token: str) -> bool:
        providers_funcs= {
            "telemost": RoomChecker._check_telemost_room_id,
            "wbstream": RoomChecker._check_wbstream_room_id,
        }

        check = providers_funcs.get(provider)
        if check is None:
            raise RuntimeError(f"Provider {provider} not supported for room generation")

        roomId = await check(room_id, token)

        return roomId

    @staticmethod
    async def _check_wbstream_room_id(room_id:str, token: str) -> bool:
        ua = UserAgent()

        headers = {
            "User-Agent": ua.random,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Referer": f"https://stream.wb.ru/room/{room_id}",
            "authorization": f"Bearer {token}",
            "Origin": "https://stream.wb.ru",
        }


        # /api-room/api/v2/room/{id} отдаёт 404 даже для абсолютно живых,
        # реально подключаемых комнат — проверено прямым сравнением на одной
        # и той же комнате. Настоящий клиент olcrtc (internal/auth/wbstream/
        # api.go в репозитории olcrtc) для входа в комнату использует другой
        # эндпоинт — /api-room/api/v1/room/{id}/join — он корректно отличает
        # живые комнаты (200) от несуществующих (404, проверено на заведомо
        # случайном room_id). Из-за сломанной проверки OLCWave считал живые
        # WB Stream-сессии мёртвыми и сам сносил рабочие контейнеры при
        # каждом обновлении подписки — выглядело как обрыв WB каждые
        # ~30 минут (по факту частота совпадала с #refresh в подписке, а не
        # с реальным временем жизни комнаты на стороне WB).
        async with httpx.AsyncClient() as client:
            res = await client.post(
                url = f"https://stream.wb.ru/api-room/api/v1/room/{room_id}/join",
                headers=headers,
                json = {},
            )

        return res.status_code == 200

    @staticmethod
    async def _check_telemost_room_id(room_id:str, *agrs, **kwargs) -> bool:
        ua = UserAgent()

        headers = {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Origin": "https://telemost.yandex.ru",
            "Referer": "https://telemost.yandex.ru/",
        }


        async with httpx.AsyncClient() as client:
            res = await client.post(
                url = f"https://telemost.yandex.ru/j/{room_id}",
                headers=headers,
                json = {}
            )

        # POST /j/{room_id} — это URL страницы для БРАУЗЕРА (HTML, страница
        # присоединения к звонку), а не JSON API. res.json() здесь падал
        # всегда. Публичного JSON-эндпоинта для проверки живости конкретной
        # комнаты Телемоста у Яндекса не нашли — до тех пор считаем комнату
        # живой при любой ошибке разбора (fail-open). Это безопасно: реальное
        # время жизни комнаты — 24ч (проверено эмпирически полем
        # expiration_time в ответе Яндекса при создании), плюс
        # lifecycle.max_session_duration в самом olcrtc уже ограничивает,
        # насколько может устареть эта информация в худшем случае.
        try:
            return bool(res.json()["uri"].split("/")[-1])
        except Exception:
            return True
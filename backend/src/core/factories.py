from functools import lru_cache

from core.config import settings
from rw.client import RemnawaveClient
from rw.service import RemnawaveService


@lru_cache
def get_remnawave_service() -> RemnawaveService:
    return RemnawaveService(
        RemnawaveClient(
            base_url=settings.RW_API_URL,
            token=settings.RW_API_TOKEN,
            caddy_token=settings.RW_CADDY_TOKEN or None,
        )
    )

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import NoReturn

from settings.service import SettingsService
from users.service import UsersService

logger = logging.getLogger(__name__)


def parse_interval(value: str) -> int:
    m = re.fullmatch(r"(\d+)([smh])", value)
    if not m:
        raise ValueError(
            f"Invalid interval format: {value!r}. "
            r"Expected format: number + unit (e.g. 30s, 10m, 4h)"
        )

    num = int(m.group(1))
    if num <= 0:
        raise ValueError(f"Interval must be positive, got {num}")

    unit = m.group(2)
    multipliers = {"s": 1, "m": 60, "h": 3600}
    return num * multipliers[unit]


class SyncManager:
    _task: asyncio.Task | None = None

    def __init__(
        self,
        users_service: UsersService,
        settings_service: SettingsService,
    ) -> None:
        self._users_service = users_service
        self._settings_service = settings_service

    async def _run(self) -> NoReturn:
        while True:
            try:
                await self._users_service.sync_with_remnawave()
                await self._settings_service.update_last_sync(
                    dt=datetime.now(timezone.utc)
                )
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("SyncManager error")

            try:
                interval_str = self._settings_service.get().sync_interval
                interval = parse_interval(interval_str)
            except Exception as e:
                print(e)
                interval = 3600

            await asyncio.sleep(interval)

    def start(self) -> None:
        if SyncManager._task is not None:
            return
        SyncManager._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

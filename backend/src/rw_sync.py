import asyncio
import logging
import re
from datetime import datetime, timezone

from settings.service import SettingsService
from users.service import Users

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

    @staticmethod
    async def _run():
        while True:
            try:
                await Users.sync_with_remnawave()
                await SettingsService.update_last_sync(datetime.now(timezone.utc))
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("SyncManager error")

            try:
                interval_str = SettingsService.get().sync_interval
                interval = parse_interval(interval_str)
            except Exception:
                interval = 3600

            await asyncio.sleep(interval)

    @staticmethod
    def start():
        if SyncManager._task is not None:
            return
        SyncManager._task = asyncio.create_task(SyncManager._run())

    @staticmethod
    async def stop():
        if SyncManager._task is None:
            return
        SyncManager._task.cancel()
        try:
            await SyncManager._task
        except asyncio.CancelledError:
            pass
        SyncManager._task = None

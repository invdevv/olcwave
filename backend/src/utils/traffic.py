import asyncio
from typing import NoReturn

from settings.service import SettingsService
from olcrtc.sdk import OlcRTCClient
from olcrtc.service import ContainersService
from users.service import UsersService


class TrafficManager:
    """Background traffic accounting and limit enforcement."""

    _last_totals: dict[str, int] = {}

    def __init__(
        self,
        user_service: UsersService,
        settings_service: SettingsService,
        olcrtc_client: OlcRTCClient,
        containers_service: ContainersService,
    ) -> None:
        self._user_service = user_service
        self._settings_service = settings_service
        self._olcrtc_client = olcrtc_client
        self._containers_service = containers_service

    @staticmethod
    def _owner_of(name: str) -> str | None:
        parts = name.split("-", 2)

        if len(parts) == 3 and parts[0] == "olcwave":
            return parts[2]

        return None

    async def _collect_deltas(self) -> dict[str, int]:
        deltas: dict[str, int] = {}
        seen: set[str] = set()

        containers = await self._olcrtc_client.all(include_stopped=False)
        for cont in containers:
            info = await cont.show()

            name = info["Name"].lstrip("/")

            if not await ContainersService.is_panel_container(cont):
                continue

            owner = TrafficManager._owner_of(name)

            if owner is None:
                continue

            seen.add(name)

            stats = await self._containers_service.get_stats(name)

            total = stats.total_bytes

            previous = self._last_totals.get(name, total)

            # container restart resets counter
            delta = (
                total - previous
                if total >= previous
                else total
            )

            self._last_totals[name] = total

            if delta > 0:
                deltas[owner] = (
                    deltas.get(owner, 0) + delta
                )

        for gone in (
            set(self._last_totals) - seen
        ):
            del self._last_totals[gone]

        return deltas

    async def _stop_user_containers(self, short_uuid: str):
        containers = await self._olcrtc_client.all(include_stopped=False)

        for cont in containers:
            info = await cont.show()

            name = info["Name"].lstrip("/")

            if not await ContainersService.is_panel_container(cont):
                continue

            if TrafficManager._owner_of(name) != short_uuid:
                continue

            try:
                await self._olcrtc_client.stop(name)

            except Exception:
                pass

    async def _tick(self):
        deltas = await self._collect_deltas()
        for short_uuid, delta in deltas.items():
            try:
                await self._user_service.add_traffic_used(short_uuid, delta)

                info = await self._user_service.get_traffic(short_uuid)

                if info.exceeded:
                    await self._stop_user_containers(short_uuid)

            except Exception:
                # one broken user should not kill loop
                continue

    async def run(self) -> NoReturn:
        while True:
            try:
                await self._tick()

            except asyncio.CancelledError:
                raise

            except Exception:
                pass

            await asyncio.sleep(
                self._settings_service.get().traffic_collect_interval
            )

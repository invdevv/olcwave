import asyncio

from config import settings
from olcrtc.sdk import OlcRTC
from olcrtc.service import Containers
from users.service import Users


class TrafficManager:
    """Background traffic accounting and limit enforcement.

    Runs inside the FastAPI lifespan. Every TRAFFIC_COLLECT_INTERVAL seconds it
    reads each running panel container's stats, accumulates the delta of
    transferred bytes onto the owning user, and stops the user's containers once
    the limit is exceeded.
    """

    # container name -> last observed total_bytes, used to accumulate deltas
    _last_totals: dict[str, int] = {}

    @staticmethod
    def _owner_of(name: str) -> str | None:
        parts = name.split("-")
        if len(parts) == 3 and parts[0] == "olcwave":
            return parts[2]
        return None

    @staticmethod
    def _collect_deltas() -> dict[str, int]:
        """Sync Docker work; returns user short_uuid -> delta bytes since last tick."""
        deltas: dict[str, int] = {}
        seen: set[str] = set()

        for cont in OlcRTC.all(include_stopped=False):
            name = cont.name
            if not name or not Containers.is_panel_container(cont):
                continue

            owner = TrafficManager._owner_of(name)
            if owner is None:
                continue

            seen.add(name)

            stats = Containers.get_stats(name)
            total = stats.total_bytes

            previous = TrafficManager._last_totals.get(name, total)
            # On restart the container's counter resets to 0; guard against negatives.
            delta = total - previous if total >= previous else total

            TrafficManager._last_totals[name] = total

            if delta > 0:
                deltas[owner] = deltas.get(owner, 0) + delta

        # Forget containers that no longer exist so restarts start clean.
        for gone in set(TrafficManager._last_totals) - seen:
            del TrafficManager._last_totals[gone]

        return deltas

    @staticmethod
    def _stop_user_containers(short_uuid: str) -> None:
        for cont in OlcRTC.all(include_stopped=False):
            name = cont.name
            if not name or not Containers.is_panel_container(cont):
                continue
            if TrafficManager._owner_of(name) == short_uuid:
                try:
                    OlcRTC.stop(name)
                except Exception:
                    pass
    @staticmethod
    async def _tick() -> None:
        deltas = await asyncio.to_thread(TrafficManager._collect_deltas)

        for short_uuid, delta in deltas.items():
            try:
                await Users.add_traffic_used(short_uuid, delta)
                info = await Users.get_traffic(short_uuid)
                if info.exceeded:
                    await asyncio.to_thread(TrafficManager._stop_user_containers, short_uuid)
            except Exception:
                # A single bad user must not break the whole loop.
                continue

    @staticmethod
    async def run() -> None:
        while True:
            try:
                await TrafficManager._tick()
            except asyncio.CancelledError:
                raise
            except Exception:
                pass
            await asyncio.sleep(settings.TRAFFIC_COLLECT_INTERVAL)

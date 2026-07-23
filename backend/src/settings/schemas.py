from pydantic import BaseModel

class RuntimeSettings(BaseModel):
    sub_name: str = "OLCWave"
    default_traffic_limit: int = 100 * 1024**3
    traffic_collect_interval: int = 10
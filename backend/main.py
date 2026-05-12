from fastapi import FastAPI, Response
import uvicorn

from rw import isUserValid, getSubscriptionSettings
from utils import getSubMD, startOlcRtc, generateRoomID, generateCmdParams, getRunningOlcRtc
from config import settings

import string
import random

app = FastAPI()

@app.get("/{short_uuid}")
async def getSub(short_uuid: str):
    sub = await isUserValid(short_uuid)
    
    if not sub:
        return Response(status_code=404)

    subSettings = await getSubscriptionSettings()

    isRunning, key, room_id = getRunningOlcRtc(short_uuid)

    if not isRunning and (key is None) and (room_id is None):
        room_id = generateRoomID(settings.OLCRTC_CARRIER)

        key = "".join([
                random.choice(string.hexdigits)
                for _ in range(64)
            ])

    subMD = getSubMD(sub, subSettings, room_id, key, short_uuid)  # pyright: ignore[reportArgumentType]

    params = generateCmdParams(room_id, key, short_uuid)  # pyright: ignore[reportArgumentType]

    startOlcRtc(params)

    return subMD

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
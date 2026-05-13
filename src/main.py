from fastapi import FastAPI, Response
import uvicorn

from rw import isUserValid
import olcmanager
import logging

logging.basicConfig(
    level=logging.INFO,
)

log = logging.getLogger("olcwave")

app = FastAPI(docs_url="", openapi_url="")

@app.get("/{short_uuid}")
async def getSub(short_uuid: str):
    sub = await isUserValid(short_uuid)
    
    if not sub:
        log.info(f"Client suuid: {short_uuid} not found in Remnawave")
        return Response(status_code=404)

    client = await olcmanager.getClient(short_uuid)
    if not client:
        log.info(f"Client suuid: {short_uuid} doesn't exist in OlcManager")
        client = await olcmanager.addClient(short_uuid, sub)
        log.info(f"Client suuid: {short_uuid} created")
    
    subscription = await olcmanager.getSubscription(client.client_id)

    return subscription

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
from fastapi import FastAPI, Response
import uvicorn

from rw import isUserValid
import olcmanager

app = FastAPI()

@app.get("/{short_uuid}")
async def getSub(short_uuid: str):
    sub = await isUserValid(short_uuid)
    
    if not sub:
        return Response(status_code=404)

    client = await olcmanager.getClient(short_uuid)
    if not client:
        client = await olcmanager.addClient(short_uuid, sub)
    
    subscription = olcmanager.getSubscription(client.client_id)

    return subscription

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
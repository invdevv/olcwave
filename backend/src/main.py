from fastapi import FastAPI

import uvicorn

from profiles.router import router as configs_router
from users.router import router as users_router
from subscriptions.router import router as subscriptions_router
from database import create_tables

async def lifespan(app: FastAPI):
    await create_tables(True)

    yield

app = FastAPI(lifespan=lifespan)  # pyright: ignore[reportArgumentType]

app.include_router(configs_router)
app.include_router(users_router)
app.include_router(subscriptions_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
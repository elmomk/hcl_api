from fastapi import FastAPI
from routers import config_creation

app = FastAPI()


app = FastAPI()

app.include_router(config_creation.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}

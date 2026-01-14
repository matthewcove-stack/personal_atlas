from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Personal Atlas")
app.include_router(router)

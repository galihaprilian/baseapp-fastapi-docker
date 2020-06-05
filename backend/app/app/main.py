from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router as api_v1_router
from app.api.api_admin.api import api_router as api_admin_router
from app.core.config import settings
from app.db import database, engine, metadata

metadata.create_all(engine)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(api_v1_router, prefix=f"{settings.API_V1_STR}")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API ADMIN
appadmin = FastAPI(
    title=settings.PROJECT_NAME + " ADMIN API",
    openapi_prefix=settings.API_ADMIN_STR,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    appadmin.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

appadmin.include_router(api_admin_router)
app.mount(settings.API_ADMIN_STR, appadmin)

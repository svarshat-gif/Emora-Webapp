from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import sentry_sdk

from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.core.exceptions import AppException, app_exception_handler, validation_exception_handler, generic_exception_handler
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.api.v1.router import api_router
from app.services.emotion.detector import emotion_detector


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("emora_starting", env=settings.APP_ENV)
    emotion_detector.load_models()

    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.APP_ENV, traces_sample_rate=0.1)
        logger.info("sentry_initialized")

    logger.info("emora_ready")
    yield
    logger.info("emora_shutdown")


app = FastAPI(
    title="Emora API",
    description="AI Emotional Companion — Backend API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# Middleware (order matters — added last runs first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routes
app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "env": settings.APP_ENV,
        "version": "1.0.0",
    }


@app.get("/", tags=["root"])
async def root():
    return {"message": "Emora API — AI Emotional Companion", "docs": "/docs"}

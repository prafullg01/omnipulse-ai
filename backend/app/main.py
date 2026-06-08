"""OmniPulse AI — FastAPI Application Entry Point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database.connection import init_db
from app.routers import auth, customers, products, events, analytics, campaigns, ai_router, support, observatory, telemetry, cart, copilot
from app.websocket.manager import router as ws_router
from app.middleware.telemetry import TelemetryMiddleware


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-Time Adaptive Customer Intelligence Operating System",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telemetry Middleware (for automatic request tracking)
app.add_middleware(TelemetryMiddleware)

# ── Routers ──
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(ai_router.router, prefix="/api/ai", tags=["AI"])
app.include_router(support.router, prefix="/api/support", tags=["Support"])
app.include_router(observatory.router, prefix="/api/observatory", tags=["Observatory"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart & Checkout"])
app.include_router(copilot.router, prefix="/api/copilot", tags=["Copilot"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/api/health")
async def health_check():
    return {"status": "operational", "platform": settings.APP_NAME, "version": settings.APP_VERSION}

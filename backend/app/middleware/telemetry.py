"""
Telemetry Middleware — Automatic Request Tracking
==================================================

Automatically tracks:
- API request latency
- Request/response sizes
- Status codes
- Error rates
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.routers.telemetry import add_latency_sample, add_log


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware to track API request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get endpoint path
        path = request.url.path
        
        # Skip telemetry endpoints to avoid infinite loops
        if path.startswith("/api/telemetry"):
            response = await call_next(request)
            return response
        
        # Skip static files and websocket
        if path.startswith("/ws") or path.startswith("/static"):
            response = await call_next(request)
            return response
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Store latency sample (remove /api/ prefix for cleaner display)
            endpoint_key = path.replace("/api/", "") if path.startswith("/api/") else path
            add_latency_sample(endpoint_key, latency_ms)
            
            # Log if slow (>1000ms)
            if latency_ms > 1000:
                add_log("WARN", "API", f"{request.method} {endpoint_key} completed in {round(latency_ms)}ms (slow)")
            
            # Log errors
            if response.status_code >= 400:
                add_log("ERROR", "API", f"{request.method} {endpoint_key} returned {response.status_code}")
            
            return response
            
        except Exception as e:
            # Log exception
            latency_ms = (time.time() - start_time) * 1000
            endpoint_key = path.replace("/api/", "") if path.startswith("/api/") else path
            
            add_log("ERROR", "API", f"{request.method} {endpoint_key} failed: {str(e)}")
            
            raise

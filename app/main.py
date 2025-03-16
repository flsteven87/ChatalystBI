from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api.api import api_router
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles as StarletteStaticFiles
from contextlib import asynccontextmanager

# Application startup and shutdown events using lifespan context manager (FastAPI best practice)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: code to run on application startup
    print("Starting ChatalystBI application...")
    
    # Setup static directories if they don't exist
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(os.path.join(static_dir, "images"), exist_ok=True)
    
    yield  # This is where the application runs
    
    # Shutdown: code to run on application shutdown
    print("Shutting down ChatalystBI application...")

# Create FastAPI application
app = FastAPI(
    title="ChatalystBI",
    description="LLM-powered Chat to BI service",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Custom static files middleware class with CORS headers
class CORSStaticFiles(StarletteStaticFiles):
    """Custom static files handler that adds CORS headers to responses"""
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            response_headers = [
                (b"access-control-allow-origin", b"*"),
                (b"access-control-allow-methods", b"GET, HEAD, OPTIONS"),
                (b"access-control-allow-headers", b"*"),
                (b"access-control-max-age", b"86400"),
            ]
            scope['response_headers'] = response_headers
        return await super().__call__(scope, receive, send)

# Mount static files directory for serving images
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", CORSStaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    """Root endpoint that returns a welcome message"""
    return {"message": "Welcome to ChatalystBI API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring system health"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

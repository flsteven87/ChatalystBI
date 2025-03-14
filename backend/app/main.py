from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

app = FastAPI(
    title="ChatalystBI",
    description="LLM-powered Chat to BI service",
    version="0.1.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")

# 自定義靜態文件中間件類，添加 CORS 頭
class CORSStaticFiles(StarletteStaticFiles):
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
os.makedirs(os.path.join(static_dir, "images"), exist_ok=True)
app.mount("/static", CORSStaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to ChatalystBI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

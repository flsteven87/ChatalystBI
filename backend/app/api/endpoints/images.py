from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from typing import List
import os
from pydantic import BaseModel
import time

router = APIRouter()

# Path to the images directory
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "images")

# 獲取基礎 URL - 優先使用環境變量，否則使用默認值
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
# 移除 API 版本路徑，如果存在
if BASE_URL.endswith("/api/v1"):
    BASE_URL = BASE_URL[:-7]

class ImageInfo(BaseModel):
    id: str
    url: str

@router.get("/{image_id}", response_model=ImageInfo)
async def get_image_info(image_id: str, request: Request):
    """
    Get information about a specific image by ID.
    
    Returns the image ID and URL that can be used to display the image.
    """
    image_path = os.path.join(IMAGES_DIR, f"{image_id}.png")
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 使用配置的基礎 URL，不依賴請求
    # 添加時間戳以防止緩存問題
    return ImageInfo(
        id=image_id,
        url=f"{BASE_URL}/static/images/{image_id}.png?t={int(time.time())}"
    )

@router.get("/", response_model=List[ImageInfo])
async def list_images(request: Request):
    """
    List all available images.
    
    Returns a list of image IDs and URLs that can be used to display the images.
    """
    images = []
    
    # 添加時間戳以防止緩存問題
    timestamp = int(time.time())
    
    # Check if the directory exists
    if os.path.exists(IMAGES_DIR):
        # List all PNG files in the directory
        for filename in os.listdir(IMAGES_DIR):
            if filename.endswith(".png"):
                image_id = filename.replace(".png", "")
                images.append(
                    ImageInfo(
                        id=image_id,
                        url=f"{BASE_URL}/static/images/{image_id}.png?t={timestamp}"
                    )
                )
    
    return images

@router.get("/test-viewer", response_class=HTMLResponse)
async def test_image_viewer(request: Request):
    """
    A simple HTML page to test viewing images.
    
    This endpoint returns an HTML page that lists all available images and displays them.
    """
    # 添加時間戳以防止緩存問題
    timestamp = int(time.time())
    
    # Get all images
    images = []
    if os.path.exists(IMAGES_DIR):
        for filename in os.listdir(IMAGES_DIR):
            if filename.endswith(".png"):
                image_id = filename.replace(".png", "")
                images.append({
                    "id": image_id,
                    "url": f"{BASE_URL}/static/images/{image_id}.png?t={timestamp}"
                })
    
    # Create an HTML page to display the images
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Viewer Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .image-container {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
            .image-info {{ margin-bottom: 10px; }}
            img {{ max-width: 100%; height: auto; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Image Viewer Test</h1>
        <p>Total images: {len(images)}</p>
        <p>Base URL: {BASE_URL}</p>
        
        {''.join([f'''
        <div class="image-container">
            <div class="image-info">
                <strong>Image ID:</strong> {img['id']}
            </div>
            <img src="{img['url']}" alt="Image {img['id']}">
            <div>
                <a href="{img['url']}" target="_blank">直接查看圖片</a>
            </div>
        </div>
        ''' for img in images])}
        
        {f'<p>No images found.</p>' if not images else ''}
    </body>
    </html>
    """
    
    return html_content 

@router.get("/test-access/{image_id}")
async def test_image_access(image_id: str, request: Request):
    """
    Test if an image can be accessed correctly.
    
    This endpoint checks if an image exists and returns information about it.
    """
    image_path = os.path.join(IMAGES_DIR, f"{image_id}.png")
    
    if not os.path.exists(image_path):
        return {
            "status": "error",
            "message": "Image not found",
            "image_id": image_id,
            "image_path": image_path,
            "exists": False
        }
    
    # 獲取圖片文件大小
    file_size = os.path.getsize(image_path)
    
    # 生成圖片 URL
    image_url = f"{BASE_URL}/static/images/{image_id}.png"
    
    return {
        "status": "success",
        "message": "Image found",
        "image_id": image_id,
        "image_path": image_path,
        "exists": True,
        "file_size": file_size,
        "base_url": BASE_URL,
        "image_url": image_url,
        "image_url_with_timestamp": f"{image_url}?t={int(time.time())}",
        "request_headers": dict(request.headers)
    } 

@router.get("/direct/{image_id}")
async def get_direct_image(image_id: str):
    """
    Serve the image directly without redirects.
    
    This endpoint returns the image file directly, with appropriate CORS headers.
    """
    image_path = os.path.join(IMAGES_DIR, f"{image_id}.png")
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        image_path, 
        media_type="image/png",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    ) 
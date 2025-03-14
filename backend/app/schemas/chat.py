from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class ImageInfo(BaseModel):
    """
    Model for image information.
    
    Attributes:
        id: The unique identifier of the image
        url: The URL to access the image
    """
    id: str
    url: str

class ChatRequest(BaseModel):
    """
    Request model for chat queries.
    
    Attributes:
        query: The natural language query from the user
        context: Optional context information for the query
    """
    query: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """
    Response model for chat queries.
    
    Attributes:
        response: The response from the AI agents
        images: Optional list of images generated during the response
    """
    response: str
    images: List[ImageInfo] = [] 
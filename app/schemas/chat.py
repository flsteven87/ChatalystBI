from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class ImageInfo(BaseModel):
    """
    Model for image information.
    
    Attributes:
        id: The unique identifier of the image
        url: The URL to access the image
    """
    id: str = Field(..., description="Unique identifier for the image")
    url: str = Field(..., description="URL to access the image")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "url": "http://localhost:8000/static/images/123e4567-e89b-12d3-a456-426614174000.png"
            }
        }

class ChatRequest(BaseModel):
    """
    Request model for chat queries.
    
    Attributes:
        query: The natural language query from the user
        context: Optional context information for the query
    """
    query: str = Field(..., description="Natural language query from the user")
    context: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Optional context information for the query"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Show me sales trends for the last quarter",
                "context": {"data_source": "sales_data"}
            }
        }

class ChatResponse(BaseModel):
    """
    Response model for chat queries.
    
    Attributes:
        response: The response from the AI agents
        images: Optional list of images generated during the response
    """
    response: str = Field(..., description="Text response from the AI agents")
    images: List[ImageInfo] = Field(
        default=[], 
        description="List of images generated during the response"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Here's the sales trend for the last quarter. We can see a 15% increase in overall revenue with the highest growth in the electronics department.",
                "images": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "url": "http://localhost:8000/static/images/123e4567-e89b-12d3-a456-426614174000.png"
                    }
                ]
            }
        } 
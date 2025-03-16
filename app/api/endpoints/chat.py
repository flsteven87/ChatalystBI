from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.crew_service import CrewService
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
crew_service = CrewService()

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest) -> ChatResponse:
    """
    Process a natural language query using multiple AI agents working together.
    
    This endpoint takes a natural language query from the user
    and processes it using a data consultant agent and a data analyst agent
    working together to provide a comprehensive response with optional visualizations.
    
    Args:
        request: The chat request containing the query and optional context
        
    Returns:
        A response containing the AI-generated answer and any visualization images
        
    Raises:
        HTTPException: If there's an error processing the query
    """
    try:
        logger.info(f"Received chat query: {request.query}")
        
        # Process the query using CrewAI agents
        result = await crew_service.process_query_with_crew(request.query, request.context)
        
        # Debug logging to track result structure
        logger.debug(f"Result from crew_service: {result}")
        
        # Construct response with text and any generated images
        response = ChatResponse(
            response=result["result"],
            images=result.get("images", [])
        )
        
        logger.info(f"Successfully processed query and returning response")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        ) 
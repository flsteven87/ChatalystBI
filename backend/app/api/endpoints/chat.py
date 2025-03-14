from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.crew_service import CrewService
import logging

# 設置日誌
logger = logging.getLogger(__name__)

router = APIRouter()
crew_service = CrewService()

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Process a query using multiple agents working together.
    
    This endpoint takes a natural language query from the user
    and processes it using a data consultant agent and a data analyst agent
    working together to provide a comprehensive response.
    """
    try:
        logger.info(f"Received chat query: {request.query}")
        
        result = await crew_service.process_query_with_crew(request.query, request.context)
        
        logger.info(f"Result from crew_service: {result}")
        logger.info(f"Result keys: {result.keys()}")
        logger.info(f"Result['result'] type: {type(result['result'])}")
        logger.info(f"Result['images'] type: {type(result.get('images', []))}")
        
        response = ChatResponse(
            response=result["result"],
            images=result.get("images", [])
        )
        
        logger.info(f"Returning response: {response}")
        
        return response
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 
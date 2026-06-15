import logging
from fastapi import APIRouter, HTTPException, Header
from app.models.schemas import SupportRequest
from app.services.ai_service import handle_request
from app.core.config import API_KEY

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/support")
def support(request: SupportRequest, x_api_key: str = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(
            status_code=401, detail="Invalid or missing API key")
    try:
        return handle_request(
            request.chatInput, request.apartment or "", request.subject or "")
    except Exception as e:
        logger.error(f"Error processing support request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )

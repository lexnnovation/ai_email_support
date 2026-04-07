import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import SupportRequest
from app.services.ai_service import handle_request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/support")
def support(request: SupportRequest):
    try:
        reply = handle_request(
            request.chatInput, request.apartment or "", request.subject or "")
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Error processing support request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )

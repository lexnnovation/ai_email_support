from typing import Optional
from pydantic import BaseModel


class SupportRequest(BaseModel):
    chatInput: str
    apartment: Optional[str] = None
    subject: Optional[str] = None

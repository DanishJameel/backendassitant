from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    gpt_type: Optional[str] = "offer_clarifier"

class GPTSelectionRequest(BaseModel):
    gpt_type: str

class SelectGPTResponse(BaseModel):
    session_id: str
    gpt_type: str
    greeting: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    fields: Optional[Dict[str, Any]] = None
    gpt_type: Optional[str] = None
    is_complete: Optional[bool] = False

class ResetResponse(BaseModel):
    status: str
    session_id: str

class CombinedSummaryResponse(BaseModel):
    combined_report: str
    sessions_data: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    sessions: int

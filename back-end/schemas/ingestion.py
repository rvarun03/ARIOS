from pydantic import BaseModel
from typing import Optional, Dict, Any

class IngestionOutput(BaseModel):
    source_type:str
    source_url: Optional[str] = None
    title: Optional[str] = None
    raw_text: str
    metadata: Dict[str, Any] = {}

    
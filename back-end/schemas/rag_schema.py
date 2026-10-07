from pydantic import BaseModel
from typing import Literal

class AskDocumentRequest(BaseModel):
    question: str
    top_k: int = 5
    source_type: str | None = None
    document_id: int | None = None
    retrieval_mode: Literal["semantic", "semantic_reranked"] = "semantic_reranked"
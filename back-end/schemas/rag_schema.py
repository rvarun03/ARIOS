from pydantic import BaseModel


class AskDocumentRequest(BaseModel):
    question: str
    top_k: int = 5
    source_type: str | None = None
    document_id: int | None = None
from pydantic import BaseModel

class DocumentIngestRequest(BaseModel):
    
    source_type:str
    source:str

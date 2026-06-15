from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from core.database import get_db


router = APIRouter(prefix="/health")

@router.get("/db")
def health_check(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "service": "ARIOS backend"
    }
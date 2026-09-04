from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from src.infrastructure.db.engine import get_session
from src.infrastructure.db.models import University

router = APIRouter(prefix="/universities", tags=["Universities"])

@router.get("/", response_model=list[University])
def list_universities(session: Session = Depends(get_session)):
    return session.exec(select(University)).all()

@router.post("/", response_model=University, status_code=status.HTTP_201_CREATED)
def create_university(name: str, session: Session = Depends(get_session)):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="University name required")
    existing = session.exec(select(University).where(University.name == name)).first()
    if existing:
        return existing
    university = University(name=name)
    session.add(university)
    session.commit()
    session.refresh(university)
    return university

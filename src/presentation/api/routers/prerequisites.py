from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from src.infrastructure.db.models import SubjectPrerequisite
from src.presentation.api.deps import get_session

router = APIRouter()

@router.get("/prerequisites/{subject_id}", response_model=List[int])
def get_prerequisites(subject_id: int, session: Session = Depends(get_session)):
    prereqs = session.exec(
        select(SubjectPrerequisite.prerequisite_subject_id)
        .where(SubjectPrerequisite.subject_id == subject_id)
    ).all()
    return [p for p in prereqs if p is not None]

@router.get("/required_for/{prerequisite_subject_id}", response_model=List[int])
def get_required_for(prerequisite_subject_id: int, session: Session = Depends(get_session)):
    required = session.exec(
        select(SubjectPrerequisite.subject_id)
        .where(SubjectPrerequisite.prerequisite_subject_id == prerequisite_subject_id)
    ).all()
    return [r for r in required if r is not None]

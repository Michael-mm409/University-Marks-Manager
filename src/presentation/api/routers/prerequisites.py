from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.infrastructure.db.models import Subject, SubjectPrerequisite
from src.presentation.api.deps import get_session

router = APIRouter()

@router.get("/prerequisites/{subject_id}", response_model=List[int])
def get_prerequisites(subject_id: int, session: Session = Depends(get_session)):
    prereqs = session.exec(
        Session.query(SubjectPrerequisite.prerequisite_subject_id)
        .filter(SubjectPrerequisite.subject_id == subject_id)
    ).all()
    return [p[0] for p in prereqs]

@router.get("/required_for/{prerequisite_subject_id}", response_model=List[int])
def get_required_for(prerequisite_subject_id: int, session: Session = Depends(get_session)):
    required = session.exec(
        Session.query(SubjectPrerequisite.subject_id)
        .filter(SubjectPrerequisite.prerequisite_subject_id == prerequisite_subject_id)
    ).all()
    return [r[0] for r in required]

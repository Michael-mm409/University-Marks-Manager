from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlmodel import col
from src.infrastructure.db.models import SubjectPrerequisite

def get_prerequisite_map(session: Session) -> Dict[int, List[int]]:
    """Return a map of subject_id -> list of prerequisite subject_ids for all subjects."""
    prereqs = session.execute(select(SubjectPrerequisite)).scalars().all()
    prereq_map: Dict[int, List[int]] = {}
    for p in prereqs:
        if p.prerequisite_subject_id is not None:
            prereq_map.setdefault(p.subject_id, []).append(p.prerequisite_subject_id)
    return prereq_map

def get_prerequisite_chain(session: Session, subject_id: int) -> List[int]:
    """Return all prerequisite subject_ids (direct and indirect) for a subject."""
    visited = set()
    def dfs(sid: int) -> None:
        rows = session.execute(
            select(SubjectPrerequisite).where(col(SubjectPrerequisite.subject_id) == sid)
        ).scalars().all()
        for p in rows:
            if p.prerequisite_subject_id is not None and p.prerequisite_subject_id not in visited:
                visited.add(p.prerequisite_subject_id)
                dfs(p.prerequisite_subject_id)
    dfs(subject_id)
    return list(visited)

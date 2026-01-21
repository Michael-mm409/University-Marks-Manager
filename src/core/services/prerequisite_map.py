from typing import Dict, List
from sqlmodel import Session
from src.infrastructure.db.models import Subject, SubjectPrerequisite

def get_prerequisite_map(session: Session) -> Dict[int, List[int]]:
    """Return a map of subject_id -> list of prerequisite subject_ids for all subjects."""
    prereqs = session.query(SubjectPrerequisite).all()
    prereq_map: Dict[int, List[int]] = {}
    for p in prereqs:
        prereq_map.setdefault(p.subject_id, []).append(p.prerequisite_subject_id)
    return prereq_map

def get_prerequisite_chain(session: Session, subject_id: int) -> List[int]:
    """Return all prerequisite subject_ids (direct and indirect) for a subject."""
    visited = set()
    def dfs(sid):
        for p in session.query(SubjectPrerequisite).filter_by(subject_id=sid):
            if p.prerequisite_subject_id not in visited:
                visited.add(p.prerequisite_subject_id)
                dfs(p.prerequisite_subject_id)
    dfs(subject_id)
    return list(visited)

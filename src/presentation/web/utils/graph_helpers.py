from __future__ import annotations

from typing import Any, Dict, List

from sqlmodel import Session, select, col

from src.infrastructure.db.models import Subject, SubjectPrerequisite
from src.presentation.web.utils.subject_helpers import infer_level_from_text


def build_subject_prerequisite_graph(session: Session, root_subject_id: int) -> Dict[str, List[dict]]:
    """Build prerequisite graph data (nodes and edges) for a subject.

    This mirrors the logic used by the subject-level prerequisite graph
    endpoint, including:
    - DFS traversal over SubjectPrerequisite
    - Shared custom nodes for short labels (5-10 chars)
    - Per-link custom nodes for longer free-text labels
    """
    root_id = int(root_subject_id)

    visited: set[int] = set()
    edges: List[dict] = []
    custom_node_map: dict[tuple, dict] = {}

    def dfs(current_id: int) -> None:
        links = session.exec(
            select(SubjectPrerequisite).where(SubjectPrerequisite.subject_id == current_id)
        ).all()
        for link in links:
            # Linked subject prerequisite
            if link.prerequisite_subject_id is not None:
                try:
                    pid = int(link.prerequisite_subject_id)
                except (TypeError, ValueError):
                    continue

                # Check link.subject_id before use
                if link.subject_id is None:
                    continue

                edges.append(
                    {
                        "from": pid,
                        "to": int(link.subject_id),
                        "type": "corequisite" if link.is_corequisite else "prerequisite",
                    }
                )
                if pid not in visited:
                    visited.add(pid)
                    dfs(pid)
            # Custom free-text prerequisite
            elif link.custom_text:
                label = str(link.custom_text).strip()
                key: tuple[Any, ...]
                if 5 <= len(label) <= 10:
                    key = ("short", label)
                else:
                    link_id_val = int(link.id) if link.id is not None else 0
                    key = ("long", label, bool(link.is_corequisite), link_id_val)

                if key not in custom_node_map:
                    custom_id = f"custom-{len(custom_node_map) + 1}"
                    level = infer_level_from_text(label)
                    node: dict = {
                        "id": custom_id,
                        "label": label,
                        "main": False,
                        "corequisite": link.is_corequisite,
                    }
                    if level is not None:
                        node["level"] = level
                    custom_node_map[key] = node

                if link.subject_id is None:
                    continue

                custom_id = custom_node_map[key]["id"]
                edges.append(
                    {
                        "from": custom_id,
                        "to": int(link.subject_id),
                        "type": "corequisite" if link.is_corequisite else "prerequisite",
                    }
                )

    dfs(root_id)

    subject_node_ids = {root_id} | visited
    subjects = (
        session.exec(select(Subject).where(col(Subject.id).in_(list(subject_node_ids)))).all()
        if subject_node_ids
        else []
    )
    by_id = {}
    for s in subjects:
        # Using explicit dot notation lets Pylance know s.id is definitely an int inside this block
        if s.id is not None:
            sid = s.id  # No need for int() call since s.id is already narrowed to an int
            by_id[sid] = {
                "object": s,
                "is_finalized": bool(getattr(s, "is_finalized", False))
            }

    nodes: List[dict] = []
    for sid in sorted(subject_node_ids):
        s_data = by_id.get(sid)
        if not s_data:
            continue
        s = s_data["object"]
        code = str(getattr(s, "subject_code", ""))
        level = infer_level_from_text(code)
        
        is_completed = s_data["is_finalized"]
        
        node: dict = {
            "id": sid,
            "label": code,
            "main": sid == root_id,
            "corequisite": False,
            "is_completed": is_completed,
        }
        if level is not None:
            node["level"] = level
        nodes.append(node)

    nodes.extend(custom_node_map.values())

    return {"nodes": nodes, "edges": edges}

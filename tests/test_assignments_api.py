"""Tests for REST API assignment endpoints and bulk import synchronization."""
import io
import json
from src.infrastructure.db.models import Subject


def test_post_assignment_syncs_subject_total(client, session, sample_data):
    """POST /api/v1/assignments/ must synchronize subjects.total_mark."""
    subject_id = sample_data["subject"].id

    payload = {
        "subject_id": subject_id,
        "assessment": "Midterm Exam",
        "weighted_mark": 35.0,
        "mark_weight": 35.0,
        "grade_type": "numeric",
        "is_exam": False,
    }

    response = client.post("/api/v1/assignments/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["assessment"] == "Midterm Exam"
    assert data["subject_id"] == subject_id

    # Verify subject total_mark is synchronized
    subject = session.get(Subject, subject_id)
    session.refresh(subject)
    assert subject.total_mark == 35.0
    assert subject.is_finalized is True


def test_put_assignment_syncs_subject_total(client, session, sample_data):
    """PUT /api/v1/assignments/{id} must synchronize subjects.total_mark."""
    subject_id = sample_data["subject"].id

    # First create an assignment
    create_payload = {
        "subject_id": subject_id,
        "assessment": "Project 1",
        "weighted_mark": 25.0,
        "mark_weight": 30.0,
        "grade_type": "numeric",
        "is_exam": False,
    }
    create_res = client.post("/api/v1/assignments/", json=create_payload)
    assert create_res.status_code == 201
    assignment_id = create_res.json()["id"]

    subject = session.get(Subject, subject_id)
    session.refresh(subject)
    assert subject.total_mark == 25.0

    # Update assignment mark
    update_payload = {
        "subject_id": subject_id,
        "assessment": "Project 1",
        "weighted_mark": 28.0,
        "mark_weight": 30.0,
        "grade_type": "numeric",
        "is_exam": False,
    }
    put_res = client.put(f"/api/v1/assignments/{assignment_id}", json=update_payload)
    assert put_res.status_code == 200

    # Verify updated total mark
    session.refresh(subject)
    assert subject.total_mark == 28.0
    assert subject.is_finalized is True


def test_delete_assignment_syncs_subject_total(client, session, sample_data):
    """DELETE /api/v1/assignments/{id} must synchronize subjects.total_mark."""
    subject_id = sample_data["subject"].id

    create_payload = {
        "subject_id": subject_id,
        "assessment": "Assignment A",
        "weighted_mark": 15.0,
        "mark_weight": 20.0,
        "grade_type": "numeric",
        "is_exam": False,
    }
    create_res = client.post("/api/v1/assignments/", json=create_payload)
    assert create_res.status_code == 201
    assignment_id = create_res.json()["id"]

    subject = session.get(Subject, subject_id)
    session.refresh(subject)
    assert subject.total_mark == 15.0

    # Delete assignment
    del_res = client.delete(f"/api/v1/assignments/{assignment_id}")
    assert del_res.status_code == 204

    # Verify subject total_mark drops back to 0.0 and is_finalized is False
    session.refresh(subject)
    assert subject.total_mark == 0.0
    assert subject.is_finalized is False


def test_bulk_import_syncs_subject_totals(client, session, sample_data):
    """Bulk import /api/v1/import/{user_id} must sync distinct subject total marks."""
    subject_id = sample_data["subject"].id
    user_id = sample_data["user"].id

    import_data = {
        "assignments": [
            {
                "id": 101,
                "subject_id": subject_id,
                "assessment": "Imported Lab 1",
                "weighted_mark": 10.0,
                "mark_weight": 10.0,
                "grade_type": "numeric",
                "is_exam": False,
            },
            {
                "id": 102,
                "subject_id": subject_id,
                "assessment": "Imported Lab 2",
                "weighted_mark": 15.0,
                "mark_weight": 15.0,
                "grade_type": "numeric",
                "is_exam": False,
            },
        ]
    }

    file_bytes = io.BytesIO(json.dumps(import_data).encode("utf-8"))
    res = client.post(
        f"/api/v1/import/{user_id}",
        files={"file": ("import.json", file_bytes, "application/json")},
    )
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Check that subjects.total_mark is synchronized
    subject = session.get(Subject, subject_id)
    session.refresh(subject)
    assert subject.total_mark == 25.0
    assert subject.is_finalized is True

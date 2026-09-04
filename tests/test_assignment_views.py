"""Tests for web assignment views and inline edit/clearing behaviors."""
from sqlmodel import Session, select

from src.infrastructure.db.models import Assignment, Subject
from src.presentation.web.views import verify_user
from src.app.main import app


def test_update_assignment_ajax_clearing_mark_empty_string(client, session, sample_data):
    """Updating an assignment with empty string weighted_mark clears it to None (Pending state)."""
    app.dependency_overrides[verify_user] = lambda: None
    try:
        subject_id = sample_data["subject"].id
        code = sample_data["subject"].subject_code
        semester = sample_data["semester"].name
        year = str(sample_data["semester"].year)

        # Create an assignment with an existing mark
        a1 = Assignment(
            subject_id=subject_id,
            assessment="Assignment 1",
            weighted_mark=20.0,
            mark_weight=20.0,
            unweighted_mark=1.0,
            grade_type="numeric",
            is_exam=False,
        )
        session.add(a1)
        session.commit()

        # Update assignment via AJAX with an empty string for weighted_mark
        url = f"/semester/{semester}/subject/{code}/assignment/Assignment 1/{year}/update"
        response = client.post(
            url,
            data={
                "code": code,
                "semester": semester,
                "year": year,
                "assessment": "Assignment 1",
                "weighted_mark": "",
                "mark_weight": "20.0",
                "grade_type": "numeric",
                "is_exam": "false",
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify assignment marks are explicitly None
        assign = session.exec(select(Assignment).where(Assignment.subject_id == subject_id)).first()
        session.refresh(assign)
        assert assign.weighted_mark is None
        assert assign.unweighted_mark is None

        # Verify subject total_mark is synchronized via GradeCalculator
        subj = session.get(Subject, subject_id)
        session.refresh(subj)
        assert subj.total_mark == 0.0
        assert subj.is_finalized is False
    finally:
        app.dependency_overrides.pop(verify_user, None)


def test_update_assignment_ajax_clearing_mark_whitespace(client, session, sample_data):
    """Updating an assignment with whitespace weighted_mark clears it to None (Pending state)."""
    app.dependency_overrides[verify_user] = lambda: None
    try:
        subject_id = sample_data["subject"].id
        code = sample_data["subject"].subject_code
        semester = sample_data["semester"].name
        year = str(sample_data["semester"].year)

        a1 = Assignment(
            subject_id=subject_id,
            assessment="Quiz 1",
            weighted_mark=15.0,
            mark_weight=15.0,
            unweighted_mark=1.0,
            grade_type="numeric",
            is_exam=False,
        )
        session.add(a1)
        session.commit()

        url = f"/semester/{semester}/subject/{code}/assignment/Quiz 1/{year}/update"
        response = client.post(
            url,
            data={
                "code": code,
                "semester": semester,
                "year": year,
                "assessment": "Quiz 1",
                "weighted_mark": "   ",
                "mark_weight": "15.0",
                "grade_type": "numeric",
                "is_exam": "false",
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        assign = session.exec(select(Assignment).where(Assignment.subject_id == subject_id)).first()
        session.refresh(assign)
        assert assign.weighted_mark is None
        assert assign.unweighted_mark is None

        subj = session.get(Subject, subject_id)
        session.refresh(subj)
        assert subj.total_mark == 0.0
        assert subj.is_finalized is False
    finally:
        app.dependency_overrides.pop(verify_user, None)


def test_update_assignment_ajax_partial_clearing_with_multiple_assignments(client, session, sample_data):
    """When one assignment is cleared, subject total_mark reflects remaining assignments and is_finalized=False."""
    app.dependency_overrides[verify_user] = lambda: None
    try:
        subject_id = sample_data["subject"].id
        code = sample_data["subject"].subject_code
        semester = sample_data["semester"].name
        year = str(sample_data["semester"].year)

        a1 = Assignment(
            subject_id=subject_id,
            assessment="Task 1",
            weighted_mark=20.0,
            mark_weight=20.0,
            unweighted_mark=1.0,
            grade_type="numeric",
            is_exam=False,
        )
        a2 = Assignment(
            subject_id=subject_id,
            assessment="Task 2",
            weighted_mark=30.0,
            mark_weight=30.0,
            unweighted_mark=1.0,
            grade_type="numeric",
            is_exam=False,
        )
        session.add_all([a1, a2])
        session.commit()

        url = f"/semester/{semester}/subject/{code}/assignment/Task 1/{year}/update"
        response = client.post(
            url,
            data={
                "code": code,
                "semester": semester,
                "year": year,
                "assessment": "Task 1",
                "weighted_mark": "",
                "mark_weight": "20.0",
                "grade_type": "numeric",
                "is_exam": "false",
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        a1_db = session.exec(select(Assignment).where(Assignment.assessment == "Task 1")).first()
        session.refresh(a1_db)
        assert a1_db.weighted_mark is None
        assert a1_db.unweighted_mark is None

        # Subject total_mark should only include Task 2 (30.0), and is_finalized should be False
        subj = session.get(Subject, subject_id)
        session.refresh(subj)
        assert subj.total_mark == 30.0
        assert subj.is_finalized is False
    finally:
        app.dependency_overrides.pop(verify_user, None)

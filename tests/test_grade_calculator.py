"""Tests for GradeCalculator service and sync_subject_total."""
from src.core.services.grade_calculator import GradeCalculator
from src.infrastructure.db.models import Assignment, Examination, Subject


def test_sync_subject_total_nonexistent_subject(session):
    """Test sync_subject_total returns None when subject does not exist."""
    calc = GradeCalculator(session)
    result = calc.sync_subject_total(99999)
    assert result is None


def test_sync_subject_total_single_assignment(session, sample_data):
    """Test sync_subject_total updates total_mark and is_finalized for a single assignment."""
    subject_id = sample_data["subject"].id

    a1 = Assignment(
        subject_id=subject_id,
        assessment="Assignment 1",
        weighted_mark=30.0,
        mark_weight=30.0,
        unweighted_mark=1.0,
        grade_type="numeric",
        is_exam=False,
    )
    session.add(a1)
    session.commit()

    calc = GradeCalculator(session)
    total = calc.sync_subject_total(subject_id)
    assert total == 30.0

    session.refresh(sample_data["subject"])
    assert sample_data["subject"].total_mark == 30.0
    assert sample_data["subject"].is_finalized is True


def test_sync_subject_total_multiple_assignments(session, sample_data):
    """Test sync_subject_total with multiple assignments."""
    subject_id = sample_data["subject"].id

    a1 = Assignment(
        subject_id=subject_id,
        assessment="Quiz 1",
        weighted_mark=15.0,
        mark_weight=20.0,
        unweighted_mark=0.75,
        grade_type="numeric",
        is_exam=False,
    )
    a2 = Assignment(
        subject_id=subject_id,
        assessment="Quiz 2",
        weighted_mark=25.0,
        mark_weight=30.0,
        unweighted_mark=0.8333,
        grade_type="numeric",
        is_exam=False,
    )
    session.add_all([a1, a2])
    session.commit()

    calc = GradeCalculator(session)
    total = calc.sync_subject_total(subject_id)
    assert total == 40.0

    session.refresh(sample_data["subject"])
    assert sample_data["subject"].total_mark == 40.0
    assert sample_data["subject"].is_finalized is True


def test_sync_subject_total_partially_graded(session, sample_data):
    """Test sync_subject_total when one assignment has no mark yet (not fully graded)."""
    subject_id = sample_data["subject"].id

    a1 = Assignment(
        subject_id=subject_id,
        assessment="Assignment 1",
        weighted_mark=20.0,
        mark_weight=25.0,
        unweighted_mark=0.80,
        grade_type="numeric",
        is_exam=False,
    )
    a2 = Assignment(
        subject_id=subject_id,
        assessment="Assignment 2",
        weighted_mark=None,
        mark_weight=25.0,
        unweighted_mark=None,
        grade_type="numeric",
        is_exam=False,
    )
    session.add_all([a1, a2])
    session.commit()

    calc = GradeCalculator(session)
    total = calc.sync_subject_total(subject_id)
    assert total == 20.0

    session.refresh(sample_data["subject"])
    assert sample_data["subject"].total_mark == 20.0
    assert sample_data["subject"].is_finalized is False


def test_sync_subject_total_update_and_delete(session, sample_data):
    """Test sync_subject_total after updating and deleting assignments."""
    subject_id = sample_data["subject"].id

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

    calc = GradeCalculator(session)
    calc.sync_subject_total(subject_id)
    session.refresh(sample_data["subject"])
    assert sample_data["subject"].total_mark == 20.0

    # Update mark
    a1.weighted_mark = 18.0
    a1.unweighted_mark = 0.90
    session.add(a1)
    session.commit()

    calc.sync_subject_total(subject_id)
    session.refresh(sample_data["subject"])
    assert sample_data["subject"].total_mark == 18.0

    # Delete assignment
    session.delete(a1)
    session.commit()

    calc.sync_subject_total(subject_id)
    session.refresh(sample_data["subject"])
    assert sample_data["subject"].total_mark == 0.0
    assert sample_data["subject"].is_finalized is False


def test_sync_subject_total_with_examination(session, sample_data):
    """Test sync_subject_total including an Examination record."""
    subject_id = sample_data["subject"].id

    a1 = Assignment(
        subject_id=subject_id,
        assessment="Assignment 1",
        weighted_mark=40.0,
        mark_weight=40.0,
        unweighted_mark=1.0,
        grade_type="numeric",
        is_exam=False,
    )
    exam = Examination(
        subject_id=subject_id,
        exam_mark=50.0,
        exam_weight=60.0,
    )
    session.add_all([a1, exam])
    session.commit()

    calc = GradeCalculator(session)
    total = calc.sync_subject_total(subject_id)
    assert total == 90.0

    session.refresh(sample_data["subject"])
    assert sample_data["subject"].total_mark == 90.0
    assert sample_data["subject"].is_finalized is True

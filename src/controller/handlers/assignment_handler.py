from typing import Optional, Tuple, Union

from model import GradeType, Semester


class AssignmentHandler:
    """
    AssignmentHandler is responsible for managing assignments within a semester.
    It provides functionality to add, delete, and modify assignments for specific subjects.

    Methods:
        __init__(semester: Semester):
            Initializes the AssignmentHandler with a given semester.
        add_assignment(subject_code: str, assessment: str, weighted_mark: Union[float, str], mark_weight: Optional[float]) -> Tuple[bool, str]:
            Adds an assignment to a subject within the semester.
        delete_assignment(subject_code: str, assessment: str) -> Tuple[bool, str]:
            Deletes an assignment from a subject within the semester.
        modify_assignment(subject_code: str, old_assessment: str, new_assessment: str, new_weighted_mark: Union[float, str], new_mark_weight: Optional[float]) -> Tuple[bool, str]:
            Modifies an existing assignment for a subject within the semester.
    """

    def __init__(self, semester: Semester):
        self.semester = semester

    def add_assignment(
        self, subject_code: str, assessment: str, weighted_mark: Union[float, str], mark_weight: Optional[float]
    ) -> Tuple[bool, str]:
        """
        Add an assignment to a subject.

        Args:
            subject_code: The subject code to add the assignment to
            assessment: Name of the assessment
            weighted_mark: The weighted mark (numeric or S/U)
            mark_weight: Weight of the assignment (None for S/U grades)

        Returns:
            Tuple of (success, message)
        """
        if not assessment or not assessment.strip():
            return False, "Assessment name cannot be empty."
        # Normalize for duplicate detection (case-insensitive, trimmed)
        normalized_new = assessment.strip().lower()

        # Fast path: check existing cached assignments if subject already loaded
        subject_cached = self.semester.subjects.get(subject_code)
        if subject_cached and any(
            a.subject_assessment.strip().lower() == normalized_new for a in subject_cached.assignments
        ):
            return False, f"Assignment '{assessment.strip()}' already exists. Use modify instead."

        # Direct DB check (case-insensitive) to catch duplicates even if cache stale
        db_conn = getattr(self.semester.data_persistence, "_conn", None)
        if db_conn is not None:
            try:
                cur = db_conn.cursor()
                cur.execute(
                    """
                    SELECT 1 FROM assignments
                    WHERE subject_code=? AND semester_name=? AND year=?
                      AND lower(trim(assessment)) = lower(trim(?))
                    LIMIT 1
                    """,
                    (subject_code, self.semester.name, self.semester.year, assessment),
                )
                if cur.fetchone():
                    return False, f"Assignment '{assessment.strip()}' already exists. Use modify instead."
            except Exception:
                # Ignore DB duplicate check failure; fallback handled by insert ignore semantics
                pass

        # Determine grade type and handle S/U grades
        if isinstance(weighted_mark, str) and weighted_mark.upper() in ["S", "U"]:
            grade_type = GradeType.SATISFACTORY if weighted_mark.upper() == "S" else GradeType.UNSATISFACTORY
            unweighted_mark = None
            final_mark_weight = None
        else:
            try:
                weighted_mark = float(weighted_mark)
                grade_type = GradeType.NUMERIC
                unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight and mark_weight > 0 else 0
                final_mark_weight = mark_weight
            except (ValueError, TypeError):
                return False, "Invalid weighted mark value."

        # Persist via SQLite helper if available
        upsert = getattr(self.semester.data_persistence, "upsert_assignment", None)
        if callable(upsert):
            upsert(
                self.semester.name,
                subject_code,
                assessment,
                weighted_mark,
                unweighted_mark,
                final_mark_weight,
                grade_type if isinstance(grade_type, GradeType) else GradeType(grade_type),
            )
            # Refresh semester subjects from cache
            self.semester.subjects = self.semester.data_persistence.data.get(self.semester.name, {})
            return True, f"Added assignment '{assessment.strip()}' to {subject_code}."
        else:
            self.semester.add_entry(
                subject_code=subject_code,
                subject_assessment=assessment,
                weighted_mark=weighted_mark,
                unweighted_mark=unweighted_mark,
                mark_weight=final_mark_weight,
                grade_type=grade_type.value if isinstance(grade_type, GradeType) else grade_type,
            )
            return True, f"Added assignment '{assessment.strip()}' to {subject_code}."
        # Fallback success
        return True, f"Added assignment '{assessment.strip()}' to {subject_code}."

    def delete_assignment(self, subject_code: str, assessment: str) -> Tuple[bool, str]:
        """
        Delete an assignment from a subject.

        Args:
            subject_code: The subject code
            assessment: Name of the assessment to delete

        Returns:
            Tuple of (success, message)
        """
        try:
            deleter = getattr(self.semester.data_persistence, "delete_assignment", None)
            if callable(deleter):
                deleter(self.semester.name, subject_code, assessment)
                self.semester.subjects = self.semester.data_persistence.data.get(self.semester.name, {})
            else:
                self.semester.delete_entry(subject_code, assessment)
            return True, f"Deleted assessment '{assessment}' from {subject_code}."
        except Exception as e:
            return False, f"Failed to delete assignment: {str(e)}"

    def modify_assignment(
        self,
        subject_code: str,
        old_assessment: str,
        new_assessment: str,
        new_weighted_mark: Union[float, str],
        new_mark_weight: Optional[float],
    ) -> Tuple[bool, str]:
        """
        Modify an existing assignment.

        Args:
            subject_code: The subject code
            old_assessment: Current assessment name
            new_assessment: New assessment name
            new_weighted_mark: New weighted mark (numeric or S/U)
            new_mark_weight: New weight of the assignment

        Returns:
            Tuple of (success, message)
        """
        if not new_assessment:
            return False, "Assessment name cannot be empty."

        subject = self.semester.subjects.get(subject_code)
        if not subject:
            return False, "Subject not found."

        # Find the assignment to modify
        assignment_to_modify = None
        for assignment in subject.assignments:
            if assignment.subject_assessment == old_assessment:
                assignment_to_modify = assignment
                break

        if not assignment_to_modify:
            return False, f"Assignment '{old_assessment}' not found."

        # Check if new name conflicts with existing assignments (excluding current one)
        if new_assessment != old_assessment:
            for assignment in subject.assignments:
                if assignment.subject_assessment == new_assessment:
                    return False, f"Assignment '{new_assessment}' already exists."

        # Determine grade type and handle S/U grades
        if isinstance(new_weighted_mark, str) and new_weighted_mark.upper() in ["S", "U"]:
            from model.enums import GradeType

            grade_type = GradeType.SATISFACTORY if new_weighted_mark.upper() == "S" else GradeType.UNSATISFACTORY
            unweighted_mark = None
            final_mark_weight = None
        else:
            try:
                new_weighted_mark = float(new_weighted_mark)
                from model.enums import GradeType

                grade_type = GradeType.NUMERIC
                unweighted_mark = (
                    round(new_weighted_mark / new_mark_weight, 4) if new_mark_weight and new_mark_weight > 0 else 0
                )
                final_mark_weight = new_mark_weight
            except (ValueError, TypeError):
                return False, "Invalid weighted mark value."

        # Update the assignment
        assignment_to_modify.subject_assessment = new_assessment
        assignment_to_modify.weighted_mark = new_weighted_mark
        assignment_to_modify.unweighted_mark = unweighted_mark
        assignment_to_modify.mark_weight = final_mark_weight
        assignment_to_modify.grade_type = grade_type

        # Persist mutation using in-place update when supported
        updater = getattr(self.semester.data_persistence, "update_assignment", None)
        grade_enum = (
            assignment_to_modify.grade_type
            if isinstance(assignment_to_modify.grade_type, GradeType)
            else GradeType(assignment_to_modify.grade_type)
        )
        if callable(updater):
            updater(
                self.semester.name,
                subject_code,
                old_assessment,
                assignment_to_modify.subject_assessment,
                assignment_to_modify.weighted_mark,
                assignment_to_modify.unweighted_mark,
                assignment_to_modify.mark_weight,
                grade_enum,
            )
            self.semester.subjects = self.semester.data_persistence.data.get(self.semester.name, {})
        else:
            # Fallback to existing upsert (delete+insert) if update not available
            upsert = getattr(self.semester.data_persistence, "upsert_assignment", None)
            if callable(upsert):
                upsert(
                    self.semester.name,
                    subject_code,
                    assignment_to_modify.subject_assessment,
                    assignment_to_modify.weighted_mark,
                    assignment_to_modify.unweighted_mark,
                    assignment_to_modify.mark_weight,
                    grade_enum,
                )
                self.semester.subjects = self.semester.data_persistence.data.get(self.semester.name, {})
            else:
                return False, "Persistence layer missing assignment update capability."

        return True, f"Modified assignment '{old_assessment}' → '{new_assessment}' in {subject_code}."


# Backward compatibility functions
def add_assignment(
    sem_obj: Semester,
    subject_code: str,
    assessment: str,
    weighted_mark: Union[float, str],
    mark_weight: Optional[float],
) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    handler = AssignmentHandler(sem_obj)
    return handler.add_assignment(subject_code, assessment, weighted_mark, mark_weight)


def delete_assignment(sem_obj: Semester, subject_code: str, assessment: str) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    handler = AssignmentHandler(sem_obj)
    return handler.delete_assignment(subject_code, assessment)


def modify_assignment(
    sem_obj: Semester,
    subject_code: str,
    old_assessment: str,
    new_assessment: str,
    new_weighted_mark: Union[float, str],
    new_mark_weight: Optional[float],
) -> Tuple[bool, str]:
    """Backward compatibility wrapper."""
    handler = AssignmentHandler(sem_obj)
    return handler.modify_assignment(subject_code, old_assessment, new_assessment, new_weighted_mark, new_mark_weight)

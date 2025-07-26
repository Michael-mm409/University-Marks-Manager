from model import GradeType, Semester


def add_assignment(sem_obj, subject_code, assessment, weighted_mark, mark_weight):
    if not assessment:
        return False, "Assessment name cannot be empty."

    # Determine grade type based on weighted_mark input
    if isinstance(weighted_mark, str):
        if weighted_mark.upper() == GradeType.SATISFACTORY.value:
            grade_type = GradeType.SATISFACTORY
            final_weighted_mark = GradeType.SATISFACTORY.value
            unweighted_mark = None
            final_mark_weight = None
        elif weighted_mark.upper() == GradeType.UNSATISFACTORY.value:
            grade_type = GradeType.UNSATISFACTORY
            final_weighted_mark = GradeType.UNSATISFACTORY.value
            unweighted_mark = None
            final_mark_weight = None
        else:
            # Try to convert string to float for numeric grades
            try:
                numeric_mark = float(weighted_mark)
                grade_type = GradeType.NUMERIC
                final_weighted_mark = numeric_mark
                unweighted_mark = round(numeric_mark / mark_weight, 4) if mark_weight > 0 else 0
                final_mark_weight = mark_weight
            except ValueError:
                return (
                    False,
                    "Invalid weighted mark format. Please provide a numeric value or a valid grade type (S/U).",
                )
    else:
        # Assume numeric grade if weighted_mark is a float
        grade_type = GradeType.NUMERIC
        final_weighted_mark = weighted_mark
        unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0
        final_mark_weight = mark_weight

    sem_obj.add_entry(
        subject_code=subject_code,
        subject_assessment=assessment,
        weighted_mark=final_weighted_mark,
        unweighted_mark=unweighted_mark,
        mark_weight=final_mark_weight,
        grade_type=grade_type,
    )
    return True, f"Added assignment '{assessment}' to {subject_code}."


def delete_assignment(sem_obj: Semester, subject_code, assessment):
    sem_obj.delete_entry(subject_code, assessment)
    return True, f"Deleted assessment '{assessment}' from {subject_code}."

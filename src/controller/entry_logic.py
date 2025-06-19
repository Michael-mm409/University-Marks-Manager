from model.semester import Semester


def add_assignment(sem_obj, subject_code, assessment, weighted_mark, mark_weight):
    if not assessment:
        return False, "Assessment name cannot be empty."
    sem_obj.add_entry(
        subject_code=subject_code,
        subject_assessment=assessment,
        weighted_mark=weighted_mark,
        unweighted_mark=round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0,
        mark_weight=mark_weight,
        grade_type="numeric",
    )
    return True, f"Added assignment '{assessment}' to {subject_code}."


def delete_assignment(sem_obj: Semester, subject_code, assessment):
    sem_obj.delete_entry(subject_code, assessment)
    return True, f"Deleted assessment '{assessment}' from {subject_code}."

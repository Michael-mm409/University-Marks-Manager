from model.domain import Semester
from model.domain.entities import Assignment, Examination, Subject
from model.repositories.data_persistence import DataPersistence


def get_all_subjects(sem_obj: Semester, data_persistence: DataPersistence) -> dict:
    """
    Retrieve all subjects for a given semester object, including synchronized subjects
    from other semesters.

    This function collects all subjects associated with the provided semester object
    (`sem_obj`) and adds any synchronized subjects from other semesters stored in the
    `data_persistence` object. Synchronized subjects are identified by the `sync_subject`
    attribute or key.

    Args:
        sem_obj (Semester): The semester object containing the current semester's subjects.
        data_persistence (DataPersistence): An object containing data for all semesters.

    Returns:
        dict: A dictionary of subjects where the keys are subject codes and the values
        are `Subject` objects. This includes both the subjects from the current semester
        and any synchronized subjects from other semesters.

    Notes:
        - If a subject is represented as a dictionary, it is converted into a `Subject`
          object with its associated assignments and examinations.
        - Synchronized subjects are only added if they are not already present in the
          current semester's subjects.
    """
    subjects = dict(sem_obj.subjects)
    for sem_name, sem_data in data_persistence.data.items():
        if sem_name == sem_obj.name:
            continue
        for subj_code, subj in sem_data.items():
            is_synced = False
            if isinstance(subj, dict):
                is_synced = subj.get("sync_subject", False)
            elif hasattr(subj, "sync_subject"):
                is_synced = subj.sync_subject
            if is_synced and subj_code not in subjects:
                if isinstance(subj, dict):
                    assignments = [Assignment(**a) for a in subj["assignments"]] if "assignments" in subj else []
                    examinations = Examination(**subj.get("examinations", {})) if "examinations" in subj else None
                    subject = Subject(
                        subject_code=subj_code,
                        subject_name=subj.get("subject_name", "N/A"),
                        assignments=assignments,
                        total_mark=subj.get("total_mark", 0.0),
                        examinations=examinations or Examination(exam_mark=0, exam_weight=100),
                        sync_subject=True,
                    )
                else:
                    subject = subj
                subjects[subj_code] = subject
    return subjects


def get_summary(subject: Subject) -> tuple:
    """
    Calculate and return a summary of marks and weights for a given subject.

    Args:
        subject (object): An object representing a subject, which contains:
            - assignments (list): A list of assignment objects, each having:
                - weighted_mark (int or float): The weighted mark of the assignment.
                - mark_weight (int or float): The weight of the assignment.
            - examinations (object, optional): An object representing the examination, with:
                - exam_mark (int or float): The mark obtained in the examination.
                - exam_weight (int or float): The weight of the examination.
            - total_mark (int or float): The total mark for the subject.

    Returns:
        tuple: A tuple containing:
            - total_weighted_mark (float): The sum of all weighted marks from assignments.
            - total_weight (float): The sum of all weights from assignments.
            - exam_mark (float): The mark obtained in the examination (0 if no examination exists).
            - exam_weight (float): The weight of the examination (100 if no examination exists).
            - total_mark (float): The total mark for the subject.
    """
    total_weighted_mark = sum(
        entry.weighted_mark for entry in subject.assignments if isinstance(entry.weighted_mark, (int, float))
    )
    total_weight = sum(
        entry.mark_weight for entry in subject.assignments if isinstance(entry.mark_weight, (int, float))
    )
    exam_mark = subject.examinations.exam_mark if subject.examinations else 0
    exam_weight = subject.examinations.exam_weight if subject.examinations else 100
    total_mark = subject.total_mark
    return total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark


def update_table(sem_obj: Semester, data_persistence: DataPersistence) -> dict:
    """
    Update the table with subjects from the current semester and synchronized subjects
    from other semesters.

    Args:
        sem_obj (Semester): The current semester object containing subjects.
        data_persistence (DataPersistence): An object containing data for all semesters.

    Returns:
        dict: A dictionary of subjects where the keys are subject codes and the values
        are `Subject` objects, including synchronized subjects.
    """
    subjects = get_all_subjects(sem_obj, data_persistence)
    records = []
    for sem_name, sem_data in data_persistence.data.items():
        if sem_name == sem_obj.name:
            continue
        synced_subjects = get_all_subjects(sem_obj, data_persistence)
        records.extend(synced_subjects.values())
    return subjects

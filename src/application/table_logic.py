import duckdb

from model import Assignment, DataPersistence, Examination, Semester, Subject


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
    # Collect all subjects from other semesters except the current one
    other_semesters = {k: v for k, v in data_persistence.data.items() if k != sem_obj.name}

    # Flatten all subjects from other semesters into a list for DuckDB processing
    records = []
    for _, sem_data in other_semesters.items():
        for subj_code, subj in sem_data.items():
            if isinstance(subj, dict):
                sync = subj.get("sync_subject", False)
            elif hasattr(subj, "sync_subject"):
                sync = subj.sync_subject
            else:
                sync = False
            records.append({"subj_code": subj_code, "subj": subj, "is_synced": sync})

    # Use DuckDB to filter for synced subjects not already in current semester
    if records:
        conn = duckdb.connect()
        # Create a temporary table from records
        conn.execute("CREATE TEMP TABLE subjects_data AS SELECT * FROM ?", [records])
        # Filter for synced subjects that aren't in current semester
        current_subjects = list(subjects.keys())
        filtered_results = conn.execute(
            """
            SELECT subj_code, subj, is_synced
            FROM subjects_data 
            WHERE is_synced = true 
            AND subj_code NOT IN (SELECT unnest(?))
        """,
            [current_subjects],
        ).fetchall()

        for subj_code, subj, _ in filtered_results:
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

        conn.close()
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
    # Prepare assignment data for DuckDB processing
    assignment_data = []
    for a in subject.assignments:
        if isinstance(a.weighted_mark, (int, float)):
            assignment_data.append(
                {
                    "weighted_mark": float(a.weighted_mark) if a.weighted_mark is not None else 0.0,
                    "mark_weight": float(a.mark_weight) if a.mark_weight is not None else 0.0,
                }
            )

    # Use DuckDB to calculate sums
    if assignment_data:
        conn = duckdb.connect()
        result = conn.execute(
            """
            SELECT 
                COALESCE(SUM(weighted_mark), 0) as total_weighted_mark,
                COALESCE(SUM(mark_weight), 0) as total_weight
            FROM ?
        """,
            [assignment_data],
        ).fetchone()
        total_weighted_mark = float(result[0]) if result and result[0] is not None else 0.0
        total_weight = float(result[1]) if result and result[1] is not None else 0.0
        conn.close()
    else:
        total_weighted_mark, total_weight = 0.0, 0.0

    exam_mark = subject.examinations.exam_mark if subject.examinations else 0
    exam_weight = subject.examinations.exam_weight if subject.examinations else 100
    total_mark = subject.total_mark
    return total_weighted_mark, total_weight, exam_mark, exam_weight, total_mark

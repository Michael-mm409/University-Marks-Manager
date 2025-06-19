from model.models import Assignment, Examination, Subject


def get_all_subjects(sem_obj, data_persistence):
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


def get_summary(subject):
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

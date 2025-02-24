from .utils import get_subject_data


def calculate_exam_mark(semester, subject_code: str) -> float:
    subject_data = get_subject_data(semester, subject_code)
    total_mark = subject_data.get("Total Mark", 0)
    assessments_sum = sum(entry.get("Weighted Mark", 0) for entry in subject_data.get("Assignments", []))

    exam_mark = max(0, round(total_mark - assessments_sum, 2))
    exam_weight = max(0, 100 - sum(entry.get("Mark Weight", 0) for entry in subject_data.get("Assignments", [])))

    subject_data["Examinations"] = {
        "Exam Mark": exam_mark,
        "Exam Weight": exam_weight
    }

    semester.data_persistence.save_data()
    return exam_mark

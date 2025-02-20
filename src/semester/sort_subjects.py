from typing import List


def sort_subjects(semester, sort_by: str = "subject_code") -> List[List[str]]:
    semester_data = semester.data_persistence.data.get(semester.name, {})
    annual_subjects = semester.data_persistence.data.get("Annual", {})
    all_subjects = {**annual_subjects, **semester_data}

    if sort_by == "subject_code":
        sorted_subjects = sorted(all_subjects.items(), key=lambda x: x[0])
    else:
        sorted_subjects = all_subjects.items()

    sorted_data_list = []
    for subject_code, subject_data in sorted_subjects:
        totals = {
            "total_weighted_mark": sum(entry.get("Weighted Mark", 0) for entry in subject_data.get("Assignments", [])),
            "total_weight": sum(entry.get("Mark Weight", 0) for entry in subject_data.get("Assignments", [])),
            "total_mark": subject_data.get("Total Mark", 0),
            "exam_data": subject_data.get("Examinations", {})
        }
        totals["exam_mark"] = totals["exam_data"].get("Exam Mark", 0)
        totals["exam_weight"] = totals["exam_data"].get("Exam Weight", 0)

        for entry in subject_data.get("Assignments"):
            sorted_data_list.append([
                subject_code,
                subject_data.get("Subject Name", "N/A"),
                entry.get("Subject Assessment", "N/A"),
                f"{entry.get('Unweighted Mark', 0):.2f}",
                f"{entry.get('Weighted Mark', 0):.2f}",
                f"{entry.get('Mark Weight', 0):.2f}%",
                f"{subject_data.get('Total Mark', 0):.2f}"
            ])

        if subject_data.get("Assignments"):
            sorted_data_list.append([
                f"Summary for {subject_code}",
                f"Assessments: {len(subject_data['Assignments'])}",
                f"Total Weighted: {totals['total_weighted_mark']:.2f}",
                f"Total Weight: {totals['total_weight']:.0f}%",
                f"Exam Mark: {totals['exam_mark']:.2f}",
                f"Exam Weight: {totals['exam_weight']:.0f}%",
                f"Total Mark: {subject_data.get('Total Mark', 0):.2f}",
            ])
            sorted_data_list.append(["=" * 20] * 7)

    return sorted_data_list
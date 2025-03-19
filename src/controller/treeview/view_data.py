from typing import List


def view_data(semester) -> List[List[str]]:
    sorted_data = semester.sort_subjects()
    print(f"Fetching data for Semester: {semester.name}, Year: {semester.year}")
    return sorted_data

from tkinter import messagebox
from typing import List, Dict, Any

from data_persistence import DataPersistence


class Semester:
    def __init__(self, name: str, year: str, data_persistence: DataPersistence):
        """Initialize Semester with its name, year, and data persistence."""
        self.name = name
        self.year = year
        self.data_persistence = data_persistence

    def __get_subject_data(self, semester: str, subject_code: str) -> Dict[str, Any]:
        """Retrieve the subject data for a given semester and subject code."""
        if semester not in self.data_persistence.data:
            self.data_persistence.data[semester] = {}
        
        if subject_code not in self.data_persistence.data[semester]:
            self.data_persistence.data[semester][subject_code] = {"Assignments": [], "Total Mark": 0, "Examinations": {"Exam Mark": 0, "Exam Weight": 100}}
        return self.data_persistence.data[semester][subject_code]
    
    def __validate_float(self, value: Any, errorr_message: str) -> float:
        """Validate the input value and return it as a float."""
        if value is None or value == "":
            return 0
        try:
            return float(value)
        except ValueError:
            messagebox.showerror("Error", errorr_message)
            return -1
        
    def add_entry(self, semester, subject_code, subject_assessment, weighted_mark, mark_weight, total_mark) -> None:
        """Add a new entry to the selected semester with assignment details."""
        # Check if subject_code is filled out
        if not subject_code:
            messagebox.showerror("Error", "Subject Code is required!")
            return
        
        subject_data = self.__get_subject_data(semester, subject_code)

        # Validate and convert input values to float
        total_mark = self.__validate_float(total_mark, "Total Mark must be a valid number.")
        
        if total_mark != -1:
            subject_data["Total Mark"] = total_mark

        weighted_mark = self.__validate_float(weighted_mark, "Weighted Mark must be a valid number.")
        mark_weight = self.__validate_float(mark_weight, "Mark Weight must be a valid number.")
        if mark_weight < 0 or mark_weight > 100:
            messagebox.showerror("Error", "Mark Weight must be between 0 and 100.")
            return
        
        unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0

        # Update assessments or add a new one
        assessments = subject_data["Assignments"]
        for entry in assessments:
            if entry.get("Subject Assessment") == subject_assessment:
                entry.update(
                    {"Unweighted Mark": unweighted_mark,
                      "Weighted Mark": weighted_mark, 
                      "Mark Weight": mark_weight})
                messagebox.showinfo("Success", "Assessment updated successfully!")
                self.data_persistence.save_data()
                return
            
        # If new assessment, add it to the list
        new_assessment = {"Subject Assessment": subject_assessment,
                          "Unweighted Mark": unweighted_mark}
        if mark_weight != -1:
            new_assessment["Weighted Mark"] = weighted_mark 
        else:
            new_assessment["Weighted Mark"] = 0
        if mark_weight != -1:
            new_assessment["Mark Weight"] = mark_weight

        assessments.append(new_assessment)
        messagebox.showinfo("Success", "Assessment added successfully!")

        # Adjust exam weight if mark weight was provided
        if mark_weight != -1:
            subject_data["Examinations"]["Exam Weight"] -= mark_weight
        self.data_persistence.save_data()

    def sort_subjects(self, sort_by: str = "subject_code") -> List[List[str]]:
        """Sort the semester subjects based on the provided sorting criteria."""
        semester_data = self.data_persistence.data.get(self.name, {})

        # Get subjects from Annual (only include them if they don't exist in the semester)
        annual_subjects = self.data_persistence.data.get("Annual", {})

        # Merge subjects: Keep semester subjects, add missing ones from Annual
        all_subjects = {**annual_subjects, **semester_data}

        # Sort the subjects based on the chosen criteria
        if sort_by == "subject_code":
            sorted_subjects = sorted(all_subjects.items(), key=lambda x: x[0])  # Sort by subject_code
        elif sort_by == "total_mark":
            sorted_subjects = sorted(all_subjects.items(), key=lambda x: x[1].get("Total Mark", 0), reverse=True)  # Sort by Total Mark
        elif sort_by == "total_weighted":
            sorted_subjects = sorted(all_subjects.items(), key=lambda x: sum(entry.get("Weighted Mark", 0) for entry in x[1].get("Assignments", [])), reverse=True)  # Sort by Total Weighted Mark
        else:
            sorted_subjects = all_subjects.items()  # No sorting if invalid sort_by value

        # Format the sorted data for display
        sorted_data_list = []
        for subject_code, subject_data in sorted_subjects:
            total_weighted_mark = sum(entry.get("Weighted Mark", 0) for entry in subject_data.get("Assignments", []))
            total_weight = sum(entry.get("Mark Weight", 0) for entry in subject_data.get("Assignments", []))
            total_mark = subject_data.get("Total Mark", 0)
            exam_data = subject_data.get("Examinations", {})
            exam_mark = exam_data.get("Exam Mark", 0)
            exam_weight = exam_data.get("Exam Weight", 0)

            # Add assignments to the list
            for entry in subject_data.get("Assignments", []):
                sorted_data_list.append([subject_code, entry.get("Subject Assessment", "N/A"),
                                        f"{entry.get('Unweighted Mark', 0):.2f}",
                                        f"{entry.get('Weighted Mark', 0):.2f}",
                                        f"{entry.get('Mark Weight', 0):.2f}%"])

            sorted_data_list.append([
                f"Summary for {subject_code}",
                f"Assessments: {len(subject_data['Assignments'])}",
                f"Total Weighted: {total_weighted_mark:.2f}",
                f"Total Weight: {total_weight:.0f}%",
                f"Total Mark: {total_mark:.0f}",
                f"Exam Mark: {exam_mark:.2f}",
                f"Exam Weight: {exam_weight:.0f}%"])
            sorted_data_list.append(["=" * 20] * 7)

        return sorted_data_list


    def view_data(self) -> List[List[str]]:
        """Retrieve and format semester data for display."""
        # Call the sort_subjects method to get sorted data
        sorted_data = self.sort_subjects()
        return sorted_data


    def calculate_exam_mark(self, subject_code: str) -> float:
        """Calculate the exam mark for a given subject based on the current semester's data."""
        subject_data = self.__get_subject_data(self.name, subject_code)
        total_mark = subject_data.get("Total Mark", 0)
        assessments_sum = sum(entry.get("Weighted Mark", 0) for entry in subject_data.get("Assignments", []))
        assessments_weight = sum(entry.get("Mark Weight", 0) for entry in subject_data.get("Assignments", []))

        # Calculate exam mark
        exam_mark = max(0, round(total_mark - assessments_sum, 2))
        exam_weight = max(0, 100 - assessments_weight)

        subject_data["Examinations"]["Exam Mark"] = exam_mark
        subject_data["Examinations"]["Exam Weight"] = exam_weight

        self.data_persistence.save_data()
        return exam_mark

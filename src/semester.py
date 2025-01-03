from tkinter import messagebox
from typing import List

from data_persistence import DataPersistence


class Semester:
    def __init__(self, name: str, year: str, data_persistence: DataPersistence):
        """Initialize Semester with its name, year, and data persistence."""
        self.name = name
        self.year = year
        self.data_persistence = data_persistence

    def add_entry(self, semester, subject_code, subject_assessment, weighted_mark, mark_weight, total_mark):
        """Add a new entry to the selected semester with assignment details."""
        # Check if subject_code is filled out
        if not subject_code:
            messagebox.showerror("Error", "Subject Code is required!")
            return

        # Ensure the data structure for the year and semester exists
        if semester not in self.data_persistence.data:
            self.data_persistence.data[semester] = {}

        if subject_code not in self.data_persistence.data[semester]:
            self.data_persistence.data[semester][subject_code] = {"Assignments": []}

        # Validate and parse `total_mark`
        if total_mark and subject_code:
            try:
                total_mark = float(total_mark)
                self.data_persistence.data[semester][subject_code]["Total Mark"] = total_mark
            except ValueError:
                messagebox.showerror("Error", "Total Mark must be a valid number.")
                return
        else:
            self.data_persistence.data[semester][subject_code]["Total Mark"] = 0

        try:
            # Validate and parse `weighted_mark` and `mark_weight`
            weighted_mark = float(weighted_mark) if weighted_mark else 0.0
            mark_weight = float(mark_weight) if mark_weight else 0.0

            # Ensure weights are within valid range
            if mark_weight < 0 or mark_weight > 100:
                messagebox.showerror("Error", "Mark Weight must be between 0 and 100!")
                return

            # Check if 'Examinations' key exists before accessing it
            if "Examinations" not in self.data_persistence.data[semester][subject_code]:
                self.data_persistence.data[semester][subject_code]["Examinations"] = {"Exam Mark": 0, "Exam Weight": 100}

            # Parse 'Examinations'
            current_exam_weight = self.data_persistence.data[semester][subject_code]["Examinations"]["Exam Weight"]
            exam_weight = float(current_exam_weight - mark_weight)

            # Print statements for debugging
            # print(f"Calculated Exam Weight for {subject_code}: {exam_weight}")

            # Ensure the data structure for 'Examinations' exists before adding to it
            print(self.data_persistence.data[semester][subject_code])

            if "Examinations" not in self.data_persistence.data[semester][subject_code]:
                self.data_persistence.data[semester][subject_code]["Examinations"]["Exam Weight"] = exam_weight
                self.data_persistence.save_data_to_json()
            print(self.data_persistence.data[semester][subject_code])

            current_exam_weight = self.data_persistence.data[semester][subject_code]["Examinations"]["Exam Weight"]
            exam_weight = current_exam_weight - mark_weight

            # Update teh "Examinations" entry with the new exam weight
            self.data_persistence.data[semester][subject_code]["Examinations"]["Exam Weight"] = exam_weight

            # Save the data to JSON after the update
            self.data_persistence.save_data_to_json()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add entry: {str(e)}")
            return

        # Calculate unweighted mark if needed
        unweighted_mark = 0
        if mark_weight != 0:
            unweighted_mark = round(weighted_mark / mark_weight, 4)


        # Add or update the assignment data
        assessments = self.data_persistence.data[semester][subject_code]["Assignments"]
        for entry in assessments:
            if entry.get("Subject Assessment") == subject_assessment:
                # If the assessment already exists, overwrite it
                entry.update({
                    "Subject Assessment": subject_assessment,
                    "Unweighted Mark": unweighted_mark,
                    "Weighted Mark": weighted_mark,
                    "Mark Weight": mark_weight,
                })
                messagebox.showinfo("Success", "Assignment updated successfully!")
                self.data_persistence.save_data_to_json()
                return

        # Check if Total Mark already exists, if so update it,
        if total_mark and "Total Mark" in self.data_persistence.data[semester][subject_code]:
            self.data_persistence.data[semester][subject_code]["Total Mark"] = total_mark
        else:
            assessments.append({
                "Subject Assessment": subject_assessment,
                "Unweighted Mark": unweighted_mark,
                "Weighted Mark": weighted_mark,
                "Mark Weight": mark_weight,
            })
            messagebox.showinfo("Success", "Assignment added successfully!")

        # Save the data to JSON
        self.data_persistence.save_data_to_json()

    def view_data(self) -> List[List[str]]:
        data_list: List[List[str]] = []
        if self.name in self.data_persistence.data:
            for subject_code, subject_data in self.data_persistence.data[self.name].items():
                total_weighted_mark = 0
                total_weight = 0
                assessments = subject_data.get("Assignments", [])

                for entry in assessments:
                    subject_assessment = entry.get("Subject Assessment", "N/A")
                    unweighted_mark = round(entry.get("Unweighted Mark", 0), 3)
                    weighted_mark = entry.get("Weighted Mark", 0)
                    mark_weight = entry.get("Mark Weight", 0)

                    # Ensure weighted_mark and mark_weight are floats before formatting
                    weighted_mark = float(weighted_mark) if isinstance(weighted_mark, (int, float)) else 0
                    mark_weight = float(mark_weight) if isinstance(mark_weight, (int, float)) else 0

                    data_list.append([
                        subject_code,
                        subject_assessment,
                        f"{unweighted_mark:.2f}",
                        f"{weighted_mark:.2f}",
                        f"{mark_weight:.2f}%"
                    ])

                    total_weighted_mark += weighted_mark
                    total_weight += mark_weight

                # Retrieve Total Mark
                total_mark = subject_data.get("Total Mark", 0)

                # Format Total Mark
                total_mark = f"{float(total_mark):.0f}" if isinstance(total_mark, (int, float)) else "N/A"

                # Print statements for debugging
                print(f"Subject Code: {subject_code}")
                print(f"Examinations Data: {subject_data.get('Examinations', {})}")

                # Add summary row after the assessments
                exam_mark = round(subject_data.get("Examinations", {}).get("Exam Mark", 0), 4)  # Updated key
                exam_weight = subject_data.get("Examinations", {}).get("Exam Weight", 0)  # Updated key

                # Format exam weight
                exam_weight = f"{exam_weight:.0f}%" if isinstance(exam_weight, (int, float)) else "N/A"

                data_list.append([
                    f"Summary for {subject_code}",
                    f"Number of Assessments: {len(assessments)}",
                    f"Total Weighted Mark: {total_weighted_mark:.2f}",
                    f"Total Mark Weight: {total_weight:.0f}%",
                    f"Total Mark: {total_mark}",
                    f"Exam Mark: {exam_mark:.2f}",
                    f"Exam Weight: {exam_weight}"
                ])

                data_list.append(["=" * 20] * 7)

        return data_list


    def calculate_exam_mark(self, subject_code: str) -> float:
        """Calculate the exam mark for a given subject based on the current semester's data."""
        for subject_code_key, subject_data in self.data_persistence.data[self.name].items():
            if subject_code_key == subject_code:
                total_mark = float(subject_data.get("Total Mark", 0))
                assessments = subject_data.get("Assignments", [])
                assessments_sum = sum(float(assessment.get("Weighted Mark", 0)) for assessment in assessments)
                assessments_weights = sum(float(assessment.get("Mark Weight", 0)) for assessment in assessments)

                # Ensure exam mark is non-negative
                exam_mark: float = round((total_mark - assessments_sum),2) if (total_mark - assessments_sum) > 0 else 0


                # Exam weight is the remaining weight
                exam_weight = max(0, 100 - assessments_weights)

                subject_data[("Examinations"
                              "")] = {"Exam Mark": exam_mark, "Exam Weight": exam_weight}
                self.data_persistence.save_data_to_json()
                return exam_mark

        return -1  # If subject code not found

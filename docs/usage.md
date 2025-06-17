# Usage Guide

## Starting the Application

1. Complete the [Installation](INSTALLATION.md) steps.
2. Activate your Python virtual environment (if used).
3. Run the application from the `src` directory:
   ```sh
   python main.py
   ```

## Main Window Overview

When the application starts, you will see the main window with the following components:

- **Year and Semester Selection:**  
  Use the dropdowns at the top to select the academic year and semester. If a year is selected for the first time, you will be prompted to choose which semesters to create (Autumn, Spring, Annual, or custom).

- **Subjects Table:**  
  The central table displays all subjects and their assessments for the selected semester. Each row shows:
  - Subject Code
  - Subject Name
  - Assessment Name
  - Unweighted Mark
  - Weighted Mark
  - Mark Weight
  - Total Mark

- **Entry Fields:**  
  Below the table, use the entry fields to input or edit:
  - Subject Code
  - Assessment Name
  - Weighted Mark (numeric or "S"/"U" for Satisfactory/Unsatisfactory)
  - Mark Weight (as a percentage)

- **Action Buttons:**  
  - **Add Subject:** Add a new subject to the current semester.
  - **Delete Subject:** Remove selected subjects from the semester.
  - **Add Entry:** Add or update an assessment entry for a subject.
  - **Delete Entry:** Remove the selected assessment entry.
  - **Calculate Exam Mark:** Calculate the exam mark for the selected subject.
  - **Set Total Mark:** Set or update the total mark for a subject.

## Example Workflows

### Adding a Subject

1. Click **Add Subject**.
2. Enter the subject code and name in the dialog.
3. (Optional) Check "Sync Subject" if you want this subject to be synchronized.
4. Click **OK** to add.

### Adding an Assessment Entry

1. Select the subject in the table or enter its code in the entry field.
2. Enter the assessment name, weighted mark, and mark weight.
3. Click **Add Entry**.

### Deleting an Entry

1. Select the row in the table corresponding to the entry you want to delete.
2. Click **Delete Entry**.

### Calculating Exam Mark

1. Enter or select the subject code.
2. Click **Calculate Exam Mark** to update the exam mark for that subject.

### Setting Total Mark

1. Enter or select the subject code.
2. Click **Set Total Mark** and enter the desired total mark in the dialog.

### Deleting a Subject

1. Click **Delete Subject**.
2. Select one or more subjects to remove in the dialog.
3. Confirm deletion.

## Tips

- **Switching Years/Semesters:**  
  Use the dropdowns to view or manage marks for different years and semesters. New years require semester selection.
- **Data Persistence:**  
  All data is saved automatically to a JSON file in the `data/` directory for each year.
- **S/U Grades:**  
  Enter "S" or "U" in the Weighted Mark field for Satisfactory/Unsatisfactory assessments.

## Troubleshooting

- If the application window does not appear, check for errors in your terminal.
- Ensure all dependencies are installed and you are using the correct Python version.
- For missing features or bugs, see [FAQ](FAQ.md) or report an issue.

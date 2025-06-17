# Student Marks Management System

## Overview
The **Student Marks Management System** is a Python-based application designed to manage and persist student marks and assessments across multiple semesters (Autumn, Spring, Annual). It provides functionality to input, edit, sync, and calculate marks for various subjects and assessments, ensuring data consistency and easy accessibility.

The application features a graphical user interface (GUI) built with `tkinter`, allowing users to interact with the system intuitively. Data is stored persistently in JSON format, enabling seamless loading and saving of records.

---

## Features
- **Semester Management**: Separate data handling for Autumn, Spring, and Annual semesters.
- **Data Persistence**: Save and load semester data to/from JSON files.
- **Synchronization**: Sync selected data from the "Annual" semester to Autumn and Spring without overwriting existing data.
- **GUI Integration**: User-friendly interface for managing subject codes, assessments, and marks.
- **Dynamic Calculations**: Automatically calculate Final Exam Marks based on Total Marks and assessment data.
- **Directory Handling**: Customizable file directory for data storage.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd student-marks-management
   ```

2. **Install Requirements**:
   Ensure you have Python 3.9 or above installed. Install any necessary packages using:
   ```bash
   pip install -r requirements.txt
   ```

   *(Optional)*: If `requirements.txt` is unavailable, ensure `tkinter` is installed on your system.

3. **Run the Application**:
   ```bash
   python main.py
   ```

---

## Usage

1. **Adding Semester Data**:
   - Enter subject codes and corresponding assessments.
   - Input unweighted marks, weighted marks, and weight percentages for each assessment.

2. **Syncing Data**:
   - Use the `sync_semesters` feature to copy missing subjects/assessments from "Annual" into Autumn and Spring.

3. **Save & Load**:
   - Save the data to the specified directory for future access.
   - Load data from existing files to continue editing.

4. **Edit Settings**:
   - Customize file storage paths by modifying the `file_directory` parameter in the `DataPersistence` class.

---

## Project Structure

```
student-marks-management/
├── data/                        # JSON data directory
├── main.py                      # Entry point for the application
├── data_persistence.py          # Data handling and persistence logic
├── semester.py                  # Semester-specific data management
├── README.md                    # Project documentation
└── requirements.txt             # Dependencies (if applicable)
```

---

## Example JSON Format

```json
{
    "Autumn": {
        "CSIT321": {
            "Assignments": [
                {
                    "Subject Assessment": "Project Requirements and Interface Presentation",
                    "Unweighted Mark": 1.0,
                    "Weighted Mark": 10.0,
                    "Mark Weight": 10.0
                }
            ]
        }
    },
    "Spring": {},
    "Annual": {}
}
```

---

## Contribution

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes and push them:
   ```bash
   git commit -m "Add your message here"
   git push origin feature/your-feature
   ```
4. Open a pull request for review.

---

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

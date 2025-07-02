# University Marks Manager

## Overview
The **University Marks Manager** is a modern Python-based web application designed to manage and track student marks and assessments across multiple academic years and semesters. Built with Streamlit, it provides an intuitive web interface for managing university coursework, calculating grades, and analyzing academic performance.

The application follows the MVC (Model-View-Controller) architectural pattern and features real-time data persistence, grade calculations, and comprehensive assignment management capabilities.

---

## Features

### 📚 Academic Management
- **Multi-Year Support**: Manage marks across different academic years
- **Semester Organization**: Separate data handling for different semesters within each year
- **Subject Management**: Add, modify, and delete university subjects
- **Assignment Tracking**: Complete CRUD operations for assignments and assessments

### 📊 Grade Management
- **Flexible Grading**: Support for both numeric grades and Satisfactory/Unsatisfactory (S/U) marking
- **Weighted Calculations**: Automatic calculation of weighted marks based on assignment weights
- **Exam Calculator**: Calculate required exam marks or derive exam performance from total marks
- **Total Mark Setting**: Set and modify total marks for subjects

### 💾 Data & Analytics
- **JSON Persistence**: Automatic saving and loading of all academic data
- **Real-time Updates**: Instant data synchronization across the application
- **Grade Analytics**: Performance summaries and grade distribution analysis
- **Data Validation**: Input validation and error handling

### 🎨 User Interface
- **Modern Web UI**: Clean, responsive Streamlit interface
- **Tabbed Navigation**: Organized sections for Overview, Management, and Analytics
- **Interactive Tables**: Dynamic data display with selection capabilities
- **Form Validation**: User-friendly error messages and input validation

---

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd University-Marks-Manager
   ```

2. **Create Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   streamlit run src/main.py
   ```

5. **Access the Application**:
   Open your web browser and navigate to `http://localhost:8501`

---

## Usage Guide

### Getting Started
1. **Select Academic Year**: Choose your current academic year from the dropdown
2. **Choose Semester**: Select the semester you want to manage
3. **Add Subjects**: Use the Management tab to add your university subjects

### Managing Assignments
1. **Add Assignments**: 
   - Enter assessment name, weighted mark, and weight percentage
   - Supports both numeric grades and S/U marking
2. **Modify Assignments**: Edit existing assignment details
3. **Delete Assignments**: Remove assignments when needed

### Grade Calculations
1. **Set Total Marks**: Define the total mark for each subject
2. **Calculate Exam Marks**: Use the Analytics tab to:
   - Calculate required exam marks for target grades
   - Derive actual exam performance from total marks
3. **View Summaries**: Check grade summaries and performance analytics

### Data Management
- All data is automatically saved to JSON files in the `data/` directory
- Data persists between sessions
- Export capabilities for backup purposes

---

## Project Structure

```
University-Marks-Manager/
├── .streamlit/                  # Streamlit configuration
│   └── config.toml             # App settings (file watcher, server config)
├── src/                        # Source code
│   ├── controller/             # Business logic layer
│   │   ├── handlers/           # Domain-specific operations
│   │   │   ├── analytics_handler.py    # Grade calculations & analytics
│   │   │   ├── assignment_handler.py   # Assignment CRUD operations
│   │   │   └── subject_handler.py      # Subject management
│   │   ├── __init__.py         # Controller exports
│   │   └── app_controller.py   # Main application controller
│   ├── model/                  # Data layer
│   │   ├── domain/             # Core business entities
│   │   │   ├── assignment.py   # Assignment entity & methods
│   │   │   ├── semester.py     # Semester entity & logic
│   │   │   └── subject.py      # Subject entity & operations
│   │   ├── repositories/       # Data persistence layer
│   │   │   └── data_persistence.py     # JSON file I/O operations
│   │   ├── enums/              # Application constants
│   │   │   ├── __init__.py     # Enum exports
│   │   │   ├── data_keys.py    # JSON structure keys
│   │   │   ├── grade_types.py  # Grade type definitions (NUMERIC, S/U)
│   │   │   └── semester_names.py       # Standard semester names
│   │   ├── types/              # Type definitions
│   │   │   └── json_types.py   # Custom type aliases
│   │   └── __init__.py         # Model exports
│   ├── view/                   # Presentation layer
│   │   ├── streamlit_views.py  # UI components & layouts
│   │   └── __init__.py         # View exports
│   └── main.py                 # Application entry point
├── data/                       # JSON data storage
│   ├── 2023.json              # Academic year data files
│   └── 2024.json              # (auto-generated)
├── assets/                     # Static resources
│   └── app_icon.ico           # Application icon
├── tests/                      # Unit & integration tests (optional)
├── docs/                       # Additional documentation (optional)
├── .gitignore                 # Git ignore patterns
├── requirements.txt           # Python dependencies
├── LICENSE                    # Project license
└── README.md                  # This documentation
```

---

## Data Format

The application stores data in JSON format with the following structure:

```json
{
  "2024": {
    "Autumn 2024": {
      "CSCI101": {
        "subject_name": "Introduction to Programming",
        "total_mark": 75.0,
        "assignments": [
          {
            "subject_assessment": "Assignment 1",
            "unweighted_mark": 18.0,
            "weighted_mark": 18.0,
            "mark_weight": 20.0,
            "grade_type": "NUMERIC"
          }
        ],
        "examinations": {
          "exam_mark": 45.0,
          "exam_weight": 60.0
        }
      }
    }
  }
}
```

---

## Configuration

### Streamlit Configuration
Create `.streamlit/config.toml` for custom settings:

```toml
[server]
fileWatcherType = "poll"
runOnSave = true

[global]
suppressDeprecationWarnings = true
```

### Data Storage
- Data files are stored in the `data/` directory
- Each academic year has its own JSON file
- Automatic backup on data modifications

---

## Development

### Architecture
The application follows the MVC pattern:
- **Model**: Data structures and business entities
- **View**: Streamlit UI components
- **Controller**: Business logic and data flow management

### Adding Features
1. **New Models**: Add to `src/model/domain/`
2. **Business Logic**: Extend controllers in `src/controller/handlers/`
3. **UI Components**: Add views to `src/view/streamlit_views.py`

### Testing
```bash
# Run unit tests (when available)
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

---

## Contributing

1. **Fork the Repository**
2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**: Follow the existing code structure and patterns
4. **Test Changes**: Ensure all functionality works correctly
5. **Commit Changes**:
   ```bash
   git commit -m "Add: description of your changes"
   ```
6. **Push and Create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions and classes
- Maintain separation of concerns (MVC pattern)

---

## Troubleshooting

### Common Issues

**Streamlit Won't Start**:
```bash
# Check if port is available
netstat -an | findstr :8501

# Use different port
streamlit run src/main.py --server.port 8502
```

**File Watching Errors**:
```bash
# Run with polling file watcher
streamlit run src/main.py --server.fileWatcherType=poll
```

**Data Not Saving**:
- Check write permissions in the `data/` directory
- Verify JSON file format validity
- Check console for error messages

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Support

For issues, questions, or contributions:
- Open an issue on the repository
- Check existing documentation
- Review the troubleshooting section

---

## Changelog

### Version 2.0.0
- Complete rewrite using Streamlit
- MVC architecture implementation
- Enhanced grade calculation features
- Modern web-based interface
- Improved data persistence

### Version 1.0.0
- Initial tkinter-based implementation
- Basic mark management functionality

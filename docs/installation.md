# Installation Guide

## Prerequisites

- Operating System: Windows, macOS, or Linux
- [Python](https://www.python.org/) 3.7 or higher
- (Optional) [Git](https://git-scm.com/) for cloning the repository

## Steps

1. **Clone the Repository**
   ```sh
   git clone https://github.com/yourusername/university-marks-manager.git
   cd university-marks-manager
   ```

2. **Create a Virtual Environment (Recommended)**
   ```sh
   python -m venv venv
   ```
   Activate the virtual environment:
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```sh
   python main.py
   ```
   *(Replace `main.py` with your actual entry-point script if different.)*

## Troubleshooting

- Ensure you are using the correct Python version (`python --version`).
- If you encounter missing module errors, check that all dependencies are installed.
- For PyQt installation issues, refer to the [PyQt documentation](https://riverbankcomputing.com/software/pyqt/intro).

## Additional Notes

- To exit the virtual environment, use `deactivate`.
- For development or testing instructions, see [Testing Guide](TESTING.md).
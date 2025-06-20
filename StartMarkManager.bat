REM filepath: c:\Users\micbm\OneDrive - University of Wollongong\UOW\Bachelor of Computer Science\Assignment Marks\University-Marks-Manager\StartMarkManager.bat
SET PYTHONPATH=%CD%
CALL conda activate UniversityMarksManager
CALL streamlit run src/main.py --server.port 8501
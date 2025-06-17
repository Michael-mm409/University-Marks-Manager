REM filepath: c:\Users\micbm\OneDrive - University of Wollongong\UOW\Bachelor of Computer Science\Assignment Marks\University-Marks-Manager\StartMarkManager.bat
SET PYTHONPATH=%CD%
CALL conda activate UniversityMarksManager
START "" pythonw src/main.py &
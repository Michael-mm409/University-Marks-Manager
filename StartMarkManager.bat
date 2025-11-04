@echo off
REM Use CONDA_ENV if set, else default to a project-specific env name
IF "%CONDA_ENV%"=="" (
	SET "CONDA_ENV=umm"
)
echo Activating Conda environment: %CONDA_ENV%
CALL conda activate "%CONDA_ENV%" && uvicorn src.app.main:app --reload
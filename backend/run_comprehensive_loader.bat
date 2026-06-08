@echo off
echo ========================================
echo OMNIPULSE AI - COMPREHENSIVE DATA LOAD
echo ========================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Delete existing database
echo.
echo Deleting existing database...
if exist omnipulse.db del /f omnipulse.db
if exist omnipulse.db-journal del /f omnipulse.db-journal
echo Database deleted.

REM Run comprehensive loader
echo.
echo Running comprehensive data loader...
echo This will load all your datasets:
echo - 5 ZIP archives
echo - omnipulse_master_events.csv
echo - ai_predictions.csv
echo.
python comprehensive_loader.py

echo.
echo ========================================
echo DONE!
echo ========================================
pause

@echo off
cd /d "c:\Users\Prafull\Desktop\OMNIPULSE AI\backend"
venv\Scripts\python.exe -u load_all_datasets.py > loader_out.txt 2>&1
echo EXIT CODE: %errorlevel%

@echo off
echo Starting Backend on Port 5000...
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
pause

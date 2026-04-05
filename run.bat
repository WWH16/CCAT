@echo off
call venv\Scripts\activate
cd ccat

:: Open main page in Chrome
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" http://127.0.0.1:8000/

:: Open student login in Edge
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" http://127.0.0.1:8000/student/login

python manage.py runserver

pause
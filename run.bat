@echo off
call venv\Scripts\activate
cd ccat
python manage.py runserver
pause

@echo off
cd /d %~dp0
"C:\ProgramData\Anaconda3\envs\RL_Test\python.exe" manage.py runserver 0.0.0.0:8888
pause

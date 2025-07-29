@echo off
cd /d "%~dp0"

REM Sensor 1
start cmd /k "python sensor1_publisher.py"

REM Sensor 2
start cmd /k "python sensor2_publisher.py"

REM Sensor 3
start cmd /k "python sensor3_publisher.py"



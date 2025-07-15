@echo off
cd /d "%~dp0"

REM Sensor 1
start cmd /k "python sensors\sensor1_publisher.py"

REM Sensor 2
start cmd /k "python sensors\sensor2_publisher.py"

REM Sensor 3
start cmd /k "python sensors\sensor3_publisher.py"

REM Subscriber
start cmd /k "python subscriber.py"

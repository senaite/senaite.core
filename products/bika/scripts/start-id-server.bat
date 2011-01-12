@set PYTHON=C:\Program Files\Plone 2\Python\python.exe
@set BIKA_BASE=C:\Program Files\Plone 2\Data
@set COUNTER_FILE=%BIKA_BASE%\var\idserver.counter
@set LOG_FILE=%BIKA_BASE%\var\idserver.log
@set PID_FILE=%BIKA_BASE%\var\idserver.pid
@set SCRIPT=%BIKA_BASE%\Products\bika\scripts\id-server.py
@set PORT=8081

"%PYTHON%" "%SCRIPT%" -f "%COUNTER_FILE%" -p "%PORT%" -l "%LOG_FILE%" %1 %2 %3 %4 %5 %6 %7

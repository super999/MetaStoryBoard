@echo off
setlocal

rem Root of dedicated Python environment
set "PY_ENV=D:\python_envs\h5_game_hack"
set "PYTHON=%PY_ENV%\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] Python interpreter not found at %PYTHON%
    echo Update PY_ENV in run_app.bat to point to your environment.
    pause
    exit /b 1
)

rem Switch working directory to the folder that contains this script
pushd "%~dp0"

rem Launch the PySide6 application
"%PYTHON%" launch.py
set "EXIT_CODE=%ERRORLEVEL%"

popd

if not "%EXIT_CODE%"=="0" (
    echo Application exited with code %EXIT_CODE%.
    pause
)

endlocal

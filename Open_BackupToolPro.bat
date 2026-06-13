@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="
set "PYTHONW_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe" set "PYTHONW_EXE=%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe"
if not defined PYTHON_EXE (
  for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
)
if not defined PYTHON_EXE (
  for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
)
if not defined PYTHONW_EXE (
  for /f "delims=" %%P in ('where pythonw 2^>nul') do if not defined PYTHONW_EXE set "PYTHONW_EXE=%%P"
)
if not defined PYTHONW_EXE set "PYTHONW_EXE=%PYTHON_EXE%"

if not defined PYTHON_EXE (
  echo Khong tim thay Python. Dang thu tu cai Python 3.12 bang winget...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo May nay chua co winget nen app khong the tu cai Python.
    echo Hay cai Python 3.12+ roi chay lai file nay.
    pause
    exit /b 1
  )
  winget install --id Python.Python.3.12 -e --scope user --silent --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo Tu cai Python that bai. Hay mo Microsoft Store/App Installer hoac cai Python 3.12 thu cong.
    pause
    exit /b 1
  )
  set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" set "PYTHONW_EXE=%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
  if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
  )
  if not defined PYTHON_EXE (
    echo Da cai Python nhung chua tim thay python.exe. Hay dong cua so nay va mo lai Open_BackupToolPro.bat.
    pause
    exit /b 1
  )
)

if not defined PYTHONW_EXE (
  for %%I in ("%PYTHON_EXE%") do if exist "%%~dpIpythonw.exe" set "PYTHONW_EXE=%%~dpIpythonw.exe"
)
if not defined PYTHONW_EXE (
  set "PYTHONW_EXE=%PYTHON_EXE%"
)

"%PYTHON_EXE%" -c "import customtkinter" >nul 2>nul
if errorlevel 1 (
  echo Dang cai thu vien customtkinter...
  "%PYTHON_EXE%" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Cai thu vien that bai. Hay kiem tra Internet hoac cai customtkinter thu cong.
    pause
    exit /b 1
  )
)

start "" "%PYTHONW_EXE%" "%~dp0backup_tool_modern.py"
endlocal

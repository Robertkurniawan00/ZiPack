@echo off
if exist "%~dp0dist\ZiPack\ZiPack.exe" (
    start "" "%~dp0dist\ZiPack\ZiPack.exe" %*
) else (
    start "" pythonw "%~dp0zipack\main.py" %*
)

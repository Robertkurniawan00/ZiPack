@echo off
if exist "%~dp0dist\ZiPack\ZiPack.exe" (
    start "" "%~dp0dist\ZiPack\ZiPack.exe" %*
) else if exist "%~dp0dist\VXArchive\VXArchive.exe" (
    start "" "%~dp0dist\VXArchive\VXArchive.exe" %*
) else (
    start "" pythonw "%~dp0zipack\main.py" %*
)

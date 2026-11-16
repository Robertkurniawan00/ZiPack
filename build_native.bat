@echo off
setlocal enabledelayedexpansion
title Build ZiPack Multi-Language Native Modules
cls
echo =====================================================================
echo   ZiPack Native Multi-Language Build System (C++, C#, C)
echo =====================================================================
echo.

set "REPO_ROOT=%~dp0"
set "GCC=C:\Users\Roku\AppData\Local\Programs\mingw64\bin\gcc.exe"
set "GXX=C:\Users\Roku\AppData\Local\Programs\mingw64\bin\g++.exe"
set "CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"

REM 1. Check G++ and GCC
where g++.exe >nul 2>&1
if %errorlevel% equ 0 set "GXX=g++.exe"
where gcc.exe >nul 2>&1
if %errorlevel% equ 0 set "GCC=gcc.exe"

REM =====================================================================
REM 1. Compile C++ Accelerator DLL (zipack_accel.dll)
REM =====================================================================
echo [1/3] Compiling C++ High-Speed Accelerator (zipack_accel.dll)...
if exist "!GXX!" (
    "!GXX!" -O3 -shared -o "%REPO_ROOT%src_native\cpp\zipack_accel.dll" "%REPO_ROOT%src_native\cpp\zipack_accel.cpp" -lkernel32
    if !errorlevel! equ 0 (
        copy /y "%REPO_ROOT%src_native\cpp\zipack_accel.dll" "%REPO_ROOT%zipack\bin\zipack_accel.dll" >nul
        echo       [OK] zipack_accel.dll built successfully.
    ) else (
        echo       [FAIL] Failed to build zipack_accel.dll.
    )
) else (
    echo       [WARN] G++ compiler not found in standard paths.
)
echo.

REM =====================================================================
REM 2. Compile C# Standalone CLI Archiver (ZiPackCLI.exe)
REM =====================================================================
echo [2/3] Compiling C# / .NET CLI Archiver (ZiPackCLI.exe)...
if exist "!CSC!" (
    "!CSC!" /nologo /target:exe /optimize+ /platform:anycpu /r:System.IO.Compression.dll,System.IO.Compression.FileSystem.dll /win32icon:"%REPO_ROOT%zipack.ico" /out:"%REPO_ROOT%src_native\csharp\ZiPackCLI.exe" "%REPO_ROOT%src_native\csharp\Program.cs"
    if !errorlevel! equ 0 (
        copy /y "%REPO_ROOT%src_native\csharp\ZiPackCLI.exe" "%REPO_ROOT%zipack\bin\ZiPackCLI.exe" >nul
        echo       [OK] ZiPackCLI.exe built successfully.
    ) else (
        echo       [FAIL] Failed to build ZiPackCLI.exe.
    )
) else (
    echo       [WARN] C# Compiler (csc.exe) not found.
)
echo.

REM =====================================================================
REM 3. Compile Pure C Win32 Launcher (ZiPackLauncher.exe)
REM =====================================================================
echo [3/3] Compiling C Win32 Lightweight Launcher (ZiPackLauncher.exe)...
if exist "!GCC!" (
    "!GCC!" -O2 -mwindows -municode -o "%REPO_ROOT%src_native\c\ZiPackLauncher.exe" "%REPO_ROOT%src_native\c\launcher.c" -luser32 -lshell32
    if !errorlevel! equ 0 (
        copy /y "%REPO_ROOT%src_native\c\ZiPackLauncher.exe" "%REPO_ROOT%zipack\bin\ZiPackLauncher.exe" >nul
        echo       [OK] ZiPackLauncher.exe built successfully.
    ) else (
        echo       [FAIL] Failed to build ZiPackLauncher.exe.
    )
) else (
    echo       [WARN] GCC compiler not found in standard paths.
)
echo.

echo =====================================================================
echo   All native multi-language binaries compiled and bundled into:
echo   - %REPO_ROOT%src_native\
echo   - %REPO_ROOT%zipack\bin\
echo =====================================================================
echo.
pause

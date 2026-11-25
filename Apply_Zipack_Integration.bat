@echo off
title Apply ZiPack Windows Shell Integration
cls
echo =====================================================================
echo   Applying ZiPack Windows Shell Associations ^& Shortcuts
echo =====================================================================
echo.
python -c "from zipack.core.shell_integration import ShellIntegration; ok, msg = ShellIntegration.register_associations(); sc_ok, sc_msg = ShellIntegration.create_shortcuts(); print('[OK] ' + msg); print('[OK] ' + sc_msg)"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] ZiPack is now registered as your default archiver!
    echo Context menus and Desktop/Start Menu shortcuts are active.
) else (
    echo.
    echo [ERROR] Failed to apply shell integration.
)
echo.
pause

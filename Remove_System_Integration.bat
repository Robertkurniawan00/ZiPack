@echo off
title Remove ZiPack System Integration
cls
echo =====================================================================
echo   ZiPack - Remove System Associations & Context Menus
echo =====================================================================
echo.
echo Removing HKCU file associations and context menu hooks...
python -c "try: from zipack.core.shell_integration import ShellIntegration; except ImportError: from vxarchive.core.shell_integration import ShellIntegration; ok, msg = ShellIntegration.unregister_associations(); print('[OK] ' + msg)"
echo.
echo Done! Associations removed cleanly.
echo.
pause

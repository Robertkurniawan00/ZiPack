@echo off
echo ===================================================
echo   Applying ZiPack Windows Shell Associations
echo ===================================================
echo.
reg import "%~dp0Zipack_Associations.reg"
if %ERRORLEVEL% EQU 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$c = @'
using System;
using System.Runtime.InteropServices;
public class WinShell {
    [DllImport(\"shell32.dll\")]
    public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);
}
'@; Add-Type -TypeDefinition $c; [WinShell]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero); [WinShell]::SHChangeNotify(0x00008000, 3, [IntPtr]::Zero, [IntPtr]::Zero)" >nul 2>&1
    echo.
    echo [SUCCESS] ZiPack is now registered as your default archiver!
    echo Context menus "Add to archive with ZiPack..." and "Extract here" are active with crisp icons.
) else (
    echo.
    echo [ERROR] Failed to import registry keys.
)
echo.
pause

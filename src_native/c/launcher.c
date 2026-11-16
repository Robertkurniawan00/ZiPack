#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <shellapi.h>
#include <wchar.h>
#include <stdbool.h>

#define ZIPACK_MUTEX_NAME L"Local\\ZiPack_SingleInstance_Mutex"
#define ZIPACK_WINDOW_TITLE L"ZiPack"

static bool FindZiPackExecutable(wchar_t* outPath, size_t maxLen) {
    wchar_t moduleDir[MAX_PATH];
    GetModuleFileNameW(NULL, moduleDir, MAX_PATH);

    // Strip file name
    wchar_t* lastSlash = wcsrchr(moduleDir, L'\\');
    if (lastSlash) {
        *lastSlash = L'\0';
    }

    // Candidate 1: Same directory as launcher
    swprintf(outPath, maxLen, L"%s\\ZiPack.exe", moduleDir);
    if (GetFileAttributesW(outPath) != INVALID_FILE_ATTRIBUTES) {
        return true;
    }

    // Candidate 2: dist\ZiPack\ZiPack.exe relative to launcher
    swprintf(outPath, maxLen, L"%s\\dist\\ZiPack\\ZiPack.exe", moduleDir);
    if (GetFileAttributesW(outPath) != INVALID_FILE_ATTRIBUTES) {
        return true;
    }

    // Candidate 3: %LOCALAPPDATA%\Programs\ZiPack\ZiPack.exe
    wchar_t localAppData[MAX_PATH];
    if (GetEnvironmentVariableW(L"LOCALAPPDATA", localAppData, MAX_PATH) > 0) {
        swprintf(outPath, maxLen, L"%s\\Programs\\ZiPack\\ZiPack.exe", localAppData);
        if (GetFileAttributesW(outPath) != INVALID_FILE_ATTRIBUTES) {
            return true;
        }
    }

    return false;
}

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow) {
    // 1. Check for single instance or activate existing window
    HANDLE hMutex = CreateMutexW(NULL, FALSE, ZIPACK_MUTEX_NAME);
    DWORD lastErr = GetLastError();

    if (hMutex != NULL && lastErr == ERROR_ALREADY_EXISTS) {
        // Application is already active - find existing window
        HWND hwndExisting = FindWindowW(NULL, ZIPACK_WINDOW_TITLE);
        if (hwndExisting != NULL) {
            if (IsIconic(hwndExisting)) {
                ShowWindow(hwndExisting, SW_RESTORE);
            }
            SetForegroundWindow(hwndExisting);

            // If arguments were passed (e.g. open file), we still allow forward execution
            if (pCmdLine == NULL || wcslen(pCmdLine) == 0) {
                CloseHandle(hMutex);
                return 0;
            }
        }
    }

    // 2. Locate ZiPack.exe
    wchar_t exePath[MAX_PATH];
    if (!FindZiPackExecutable(exePath, MAX_PATH)) {
        MessageBoxW(
            NULL,
            L"Could not locate 'ZiPack.exe'.\nPlease verify that ZiPack is properly installed.",
            L"ZiPack Launcher Error",
            MB_ICONERROR | MB_OK
        );
        if (hMutex) CloseHandle(hMutex);
        return 1;
    }

    // 3. Launch ZiPack with passed arguments
    SHELLEXECUTEINFOW sei = { sizeof(sei) };
    sei.cbSize = sizeof(sei);
    sei.fMask = SEE_MASK_DEFAULT;
    sei.hwnd = NULL;
    sei.lpVerb = L"open";
    sei.lpFile = exePath;
    sei.lpParameters = pCmdLine;
    sei.lpDirectory = NULL;
    sei.nShow = SW_SHOWNORMAL;

    if (!ShellExecuteExW(&sei)) {
        DWORD err = GetLastError();
        wchar_t errMsg[256];
        swprintf(errMsg, 256, L"Failed to start ZiPack (Error code: %lu).", err);
        MessageBoxW(NULL, errMsg, L"ZiPack Launcher Error", MB_ICONERROR | MB_OK);
        if (hMutex) CloseHandle(hMutex);
        return 2;
    }

    if (hMutex) {
        CloseHandle(hMutex);
    }
    return 0;
}

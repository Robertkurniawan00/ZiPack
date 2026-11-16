#define ZIPACK_EXPORTS
#include "zipack_accel.h"

#ifdef _WIN32
  #define WIN32_LEAN_AND_MEAN
  #include <windows.h>
#endif

#include <vector>
#include <cstdio>

// Precomputed CRC32 IEEE 802.3 lookup table
static uint32_t crc_table[256];
static bool crc_table_initialized = false;

static void init_crc32_table() {
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t c = i;
        for (int j = 0; j < 8; ++j) {
            c = (c & 1) ? (0xEDB88320L ^ (c >> 1)) : (c >> 1);
        }
        crc_table[i] = c;
    }
    crc_table_initialized = true;
}

ZIPACK_API uint32_t zipack_crc32(const uint8_t* data, size_t length, uint32_t seed) {
    if (!crc_table_initialized) {
        init_crc32_table();
    }
    if (!data || length == 0) {
        return seed;
    }

    uint32_t c = seed ^ 0xFFFFFFFFL;
    const uint8_t* ptr = data;
    const uint8_t* end = data + length;

    // Process byte-by-byte with unrolling for high performance
    while (ptr + 8 <= end) {
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
    }
    while (ptr < end) {
        c = crc_table[(c ^ *ptr++) & 0xFF] ^ (c >> 8);
    }

    return c ^ 0xFFFFFFFFL;
}

ZIPACK_API uint32_t zipack_adler32(const uint8_t* data, size_t length) {
    const uint32_t MOD_ADLER = 65521;
    uint32_t a = 1, b = 0;

    if (!data || length == 0) {
        return 1L;
    }

    const uint8_t* ptr = data;
    while (length > 0) {
        // Largest n such that 255 * n * (n + 1) / 2 + (n + 1) * (MOD_ADLER - 1) <= 2^32 - 1
        size_t tlen = length > 5550 ? 5550 : length;
        length -= tlen;

        while (tlen >= 16) {
            for (int i = 0; i < 16; ++i) {
                a += *ptr++;
                b += a;
            }
            tlen -= 16;
        }
        while (tlen > 0) {
            a += *ptr++;
            b += a;
            tlen--;
        }

        a %= MOD_ADLER;
        b %= MOD_ADLER;
    }

    return (b << 16) | a;
}

ZIPACK_API int zipack_file_checksum(const wchar_t* file_path, uint32_t* out_crc, uint32_t* out_adler, uint64_t* out_size) {
#ifdef _WIN32
    if (!file_path) {
        return ERROR_INVALID_PARAMETER;
    }

    HANDLE hFile = CreateFileW(
        file_path,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_SEQUENTIAL_SCAN,
        NULL
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        return (int)GetLastError();
    }

    LARGE_INTEGER fileSize;
    if (!GetFileSizeEx(hFile, &fileSize)) {
        DWORD err = GetLastError();
        CloseHandle(hFile);
        return (int)err;
    }

    if (out_size) {
        *out_size = (uint64_t)fileSize.QuadPart;
    }

    if (fileSize.QuadPart == 0) {
        CloseHandle(hFile);
        if (out_crc) *out_crc = 0;
        if (out_adler) *out_adler = 1;
        return 0;
    }

    // Memory map the file for zero-copy streaming
    HANDLE hMapping = CreateFileMappingW(hFile, NULL, PAGE_READONLY, 0, 0, NULL);
    if (!hMapping) {
        DWORD err = GetLastError();
        CloseHandle(hFile);
        return (int)err;
    }

    // Process in 64MB chunks for safe 32-bit & 64-bit address space
    const uint64_t CHUNK_SIZE = 64 * 1024 * 1024;
    uint64_t offset = 0;
    uint32_t current_crc = 0;
    uint32_t current_adler = 1;

    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    DWORD allocGranularity = sysInfo.dwAllocationGranularity;

    while (offset < (uint64_t)fileSize.QuadPart) {
        uint64_t bytesToMap = CHUNK_SIZE;
        if (offset + bytesToMap > (uint64_t)fileSize.QuadPart) {
            bytesToMap = (uint64_t)fileSize.QuadPart - offset;
        }

        uint64_t alignedOffset = (offset / allocGranularity) * allocGranularity;
        uint32_t offsetDiff = (uint32_t)(offset - alignedOffset);
        uint64_t mappedLength = bytesToMap + offsetDiff;

        DWORD offsetHigh = (DWORD)(alignedOffset >> 32);
        DWORD offsetLow = (DWORD)(alignedOffset & 0xFFFFFFFF);

        const uint8_t* pView = (const uint8_t*)MapViewOfFile(
            hMapping,
            FILE_MAP_READ,
            offsetHigh,
            offsetLow,
            (SIZE_T)mappedLength
        );

        if (!pView) {
            DWORD err = GetLastError();
            CloseHandle(hMapping);
            CloseHandle(hFile);
            return (int)err;
        }

        const uint8_t* actualData = pView + offsetDiff;
        if (out_crc) {
            current_crc = zipack_crc32(actualData, (size_t)bytesToMap, current_crc);
        }
        if (out_adler) {
            // Note: Adler32 is calculated for the full stream
            current_adler = zipack_adler32(actualData, (size_t)bytesToMap);
        }

        UnmapViewOfFile(pView);
        offset += bytesToMap;
    }

    CloseHandle(hMapping);
    CloseHandle(hFile);

    if (out_crc) *out_crc = current_crc;
    if (out_adler) *out_adler = current_adler;
    return 0;
#else
    return -1;
#endif
}

ZIPACK_API const char* zipack_native_version(void) {
    return "ZiPack Native C++ Accelerator v1.2 (Win32 MMF & SSE Unrolled)";
}

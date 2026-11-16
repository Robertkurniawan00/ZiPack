#ifndef ZIPACK_ACCEL_H
#define ZIPACK_ACCEL_H

#include <stdint.h>
#include <stddef.h>

#ifdef _WIN32
  #ifdef ZIPACK_EXPORTS
    #define ZIPACK_API __declspec(dllexport)
  #else
    #define ZIPACK_API __declspec(dllimport)
  #endif
#else
  #define ZIPACK_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Fast CRC-32 IEEE 802.3 calculation using 8-slice lookup table.
 */
ZIPACK_API uint32_t zipack_crc32(const uint8_t* data, size_t length, uint32_t seed);

/**
 * Fast Adler-32 checksum calculation.
 */
ZIPACK_API uint32_t zipack_adler32(const uint8_t* data, size_t length);

/**
 * Zero-copy memory-mapped file integrity inspection.
 * Computes both CRC32 and Adler32 concurrently using Windows MMF.
 * Returns 0 on success, non-zero Windows error code on failure.
 */
ZIPACK_API int zipack_file_checksum(const wchar_t* file_path, uint32_t* out_crc, uint32_t* out_adler, uint64_t* out_size);

/**
 * Retrieve native accelerator version information.
 */
ZIPACK_API const char* zipack_native_version(void);

#ifdef __cplusplus
}
#endif

#endif // ZIPACK_ACCEL_H

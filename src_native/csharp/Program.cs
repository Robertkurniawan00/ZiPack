using System;
using System.IO;
using System.IO.Compression;
using System.Diagnostics;
using System.Threading;

namespace ZiPackCLI
{
    class Program
    {
        static int Main(string[] args)
        {
            Console.Title = "ZiPack Native CLI Tool (C# / .NET)";

            if (args.Length == 0)
            {
                PrintUsage();
                return 0;
            }

            string command = args[0].ToLowerInvariant().TrimStart('-', '/');

            try
            {
                switch (command)
                {
                    case "help":
                    case "?":
                    case "h":
                        PrintUsage();
                        return 0;

                    case "version":
                    case "v":
                        Console.WriteLine("ZiPack CLI Tool v2.0 (Built with C# / .NET Framework 4.8)");
                        Console.WriteLine("Copyright (C) 2026 ZiPack Studio. All rights reserved.");
                        return 0;

                    case "extract":
                    case "x":
                        if (args.Length < 2)
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine("Error: Missing archive path for extract command.");
                            Console.ResetColor();
                            return 1;
                        }
                        return ExtractArchive(args[1], args.Length > 2 ? args[2] : null);

                    case "compress":
                    case "a":
                    case "c":
                        if (args.Length < 3)
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine("Error: Usage: zipack compress <output.zip> <source_file_or_dir>");
                            Console.ResetColor();
                            return 1;
                        }
                        return CompressArchive(args[1], args[2]);

                    case "list":
                    case "l":
                        if (args.Length < 2)
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine("Error: Missing archive path to list.");
                            Console.ResetColor();
                            return 1;
                        }
                        return ListArchive(args[1]);

                    case "test":
                    case "t":
                        if (args.Length < 2)
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine("Error: Missing archive path to test.");
                            Console.ResetColor();
                            return 1;
                        }
                        return TestArchive(args[1]);

                    case "benchmark":
                    case "bench":
                        int mb = 50;
                        if (args.Length > 1) int.TryParse(args[1], out mb);
                        return RunBenchmark(mb);

                    default:
                        Console.ForegroundColor = ConsoleColor.Yellow;
                        Console.WriteLine("Unknown command: " + args[0]);
                        Console.ResetColor();
                        PrintUsage();
                        return 1;
                }
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("Fatal error: " + ex.Message);
                Console.ResetColor();
                return 2;
            }
        }

        static void PrintUsage()
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("==================================================================");
            Console.WriteLine("    ZiPack Native CLI Tool (C# / .NET High-Performance Engine)");
            Console.WriteLine("==================================================================");
            Console.ResetColor();
            Console.WriteLine("Usage: ZiPackCLI <command> [options] [arguments]\n");
            Console.WriteLine("Commands:");
            Console.WriteLine("  extract, x <archive> [target]    Extract archive contents with auto-clean");
            Console.WriteLine("  compress, a <out.zip> <src>      Compress file or directory to ZIP");
            Console.WriteLine("  list, l <archive>                Display archive table of contents");
            Console.WriteLine("  test, t <archive>                Verify archive stream integrity");
            Console.WriteLine("  benchmark [sizeMB]               Run .NET Deflate/Zip CPU benchmark");
            Console.WriteLine("  version, v                       Display version and runtime information");
            Console.WriteLine("  help, ?                          Show this help message\n");
            Console.WriteLine("Examples:");
            Console.WriteLine("  ZiPackCLI extract \"project.zip\" \"C:\\MyFolder\"");
            Console.WriteLine("  ZiPackCLI compress \"backup.zip\" \"D:\\ImportantDocs\"");
            Console.WriteLine("  ZiPackCLI list \"archive.zip\"");
        }

        static int ExtractArchive(string archivePath, string destination)
        {
            if (!File.Exists(archivePath))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("File not found: " + archivePath);
                Console.ResetColor();
                return 1;
            }

            if (string.IsNullOrEmpty(destination))
            {
                destination = Path.Combine(
                    Path.GetDirectoryName(Path.GetFullPath(archivePath)),
                    Path.GetFileNameWithoutExtension(archivePath)
                );
            }

            Console.WriteLine("Opening: " + Path.GetFileName(archivePath));
            Console.WriteLine("Target:  " + destination);
            Directory.CreateDirectory(destination);

            Stopwatch sw = Stopwatch.StartNew();
            int fileCount = 0;
            long totalBytes = 0;

            using (ZipArchive zip = ZipFile.OpenRead(archivePath))
            {
                foreach (ZipArchiveEntry entry in zip.Entries)
                {
                    // Guard against Zip Slip
                    string fullDestPath = Path.GetFullPath(Path.Combine(destination, entry.FullName));
                    if (!fullDestPath.StartsWith(Path.GetFullPath(destination) + Path.DirectorySeparatorChar))
                    {
                        Console.ForegroundColor = ConsoleColor.Yellow;
                        Console.WriteLine("Warning: Blocked Zip Slip path: " + entry.FullName);
                        Console.ResetColor();
                        continue;
                    }

                    if (string.IsNullOrEmpty(entry.Name))
                    {
                        Directory.CreateDirectory(fullDestPath);
                        continue;
                    }

                    Directory.CreateDirectory(Path.GetDirectoryName(fullDestPath));
                    entry.ExtractToFile(fullDestPath, true);
                    fileCount++;
                    totalBytes += entry.Length;
                }
            }

            sw.Stop();
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine(string.Format("Success: Extracted {0} files ({1:F2} MB) in {2} ms.",
                fileCount, totalBytes / (1024.0 * 1024.0), sw.ElapsedMilliseconds));
            Console.ResetColor();
            return 0;
        }

        static int CompressArchive(string outputZip, string sourcePath)
        {
            if (!File.Exists(sourcePath) && !Directory.Exists(sourcePath))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("Source does not exist: " + sourcePath);
                Console.ResetColor();
                return 1;
            }

            string outDir = Path.GetDirectoryName(Path.GetFullPath(outputZip));
            if (!string.IsNullOrEmpty(outDir))
            {
                Directory.CreateDirectory(outDir);
            }

            if (File.Exists(outputZip))
            {
                File.Delete(outputZip);
            }

            Console.WriteLine("Creating: " + outputZip);
            Console.WriteLine("Source:   " + sourcePath);

            Stopwatch sw = Stopwatch.StartNew();

            if (Directory.Exists(sourcePath))
            {
                ZipFile.CreateFromDirectory(sourcePath, outputZip, CompressionLevel.Optimal, false);
            }
            else
            {
                using (ZipArchive zip = ZipFile.Open(outputZip, ZipArchiveMode.Create))
                {
                    zip.CreateEntryFromFile(sourcePath, Path.GetFileName(sourcePath), CompressionLevel.Optimal);
                }
            }

            sw.Stop();
            FileInfo fi = new FileInfo(outputZip);
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine(string.Format("Success: Archive created ({0:F2} KB) in {1} ms.",
                fi.Length / 1024.0, sw.ElapsedMilliseconds));
            Console.ResetColor();
            return 0;
        }

        static int ListArchive(string archivePath)
        {
            if (!File.Exists(archivePath))
            {
                Console.WriteLine("File not found: " + archivePath);
                return 1;
            }

            Console.WriteLine("Contents of: " + archivePath);
            Console.WriteLine(new string('-', 75));
            Console.WriteLine(string.Format("{0,-45} {1,12} {2,14}", "Name", "Size", "Compressed"));
            Console.WriteLine(new string('-', 75));

            long totalSize = 0;
            long totalCompressed = 0;
            int count = 0;

            using (ZipArchive zip = ZipFile.OpenRead(archivePath))
            {
                foreach (ZipArchiveEntry entry in zip.Entries)
                {
                    string name = entry.FullName;
                    if (name.Length > 44) name = "..." + name.Substring(name.Length - 41);
                    Console.WriteLine(string.Format("{0,-45} {1,12:N0} {2,14:N0}", name, entry.Length, entry.CompressedLength));
                    totalSize += entry.Length;
                    totalCompressed += entry.CompressedLength;
                    count++;
                }
            }

            Console.WriteLine(new string('-', 75));
            Console.WriteLine(string.Format("Total: {0} entries | {1:N0} bytes -> {2:N0} bytes ({3:P1} ratio)",
                count, totalSize, totalCompressed, totalSize > 0 ? (double)totalCompressed / totalSize : 0));
            return 0;
        }

        static int TestArchive(string archivePath)
        {
            if (!File.Exists(archivePath))
            {
                Console.WriteLine("File not found: " + archivePath);
                return 1;
            }

            Console.Write("Testing integrity of " + Path.GetFileName(archivePath) + "... ");
            Stopwatch sw = Stopwatch.StartNew();
            byte[] buffer = new byte[65536];

            try
            {
                using (ZipArchive zip = ZipFile.OpenRead(archivePath))
                {
                    foreach (ZipArchiveEntry entry in zip.Entries)
                    {
                        using (Stream s = entry.Open())
                        {
                            while (s.Read(buffer, 0, buffer.Length) > 0)
                            {
                                // Stream verification
                            }
                        }
                    }
                }
                sw.Stop();
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine(string.Format("PASSED ({0} ms)", sw.ElapsedMilliseconds));
                Console.ResetColor();
                return 0;
            }
            catch (Exception ex)
            {
                sw.Stop();
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("CORRUPT: " + ex.Message);
                Console.ResetColor();
                return 2;
            }
        }

        static int RunBenchmark(int sizeMB)
        {
            Console.WriteLine(string.Format("Running .NET Deflate Benchmark ({0} MB payload)...", sizeMB));
            byte[] data = new byte[sizeMB * 1024 * 1024];
            new Random(42).NextBytes(data);

            Stopwatch sw = Stopwatch.StartNew();
            long compressedSize = 0;
            using (MemoryStream ms = new MemoryStream())
            {
                using (GZipStream gz = new GZipStream(ms, CompressionMode.Compress, true))
                {
                    gz.Write(data, 0, data.Length);
                }
                compressedSize = ms.Length;
            }
            sw.Stop();

            double speed = (double)sizeMB / (sw.ElapsedMilliseconds / 1000.0);
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine(string.Format("Throughput: {0:F2} MB/s | Ratio: {1:P1} | Time: {2} ms",
                speed, (double)compressedSize / data.Length, sw.ElapsedMilliseconds));
            Console.ResetColor();
            return 0;
        }
    }
}

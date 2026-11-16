# ZiPack PowerShell Automation Module
# Provides native cmdlets for compressing, extracting, and testing archives with ZiPack engine.

Set-StrictMode -Version Latest

function Get-ZiPackVersion {
    <#
    .SYNOPSIS
    Returns version and architectural information for the ZiPack engine.
    #>
    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        ModuleName    = "ZiPack"
        Version       = "2.0.0"
        Engine        = "PyQt6 / C++ Accelerator / C# CLI / C Win32"
        NativeAccel   = (Test-Path "$PSScriptRoot\..\..\zipack\bin\zipack_accel.dll") -or (Test-Path "$PSScriptRoot\..\..\src_native\cpp\zipack_accel.dll")
        CliTool       = (Test-Path "$PSScriptRoot\..\..\zipack\bin\ZiPackCLI.exe") -or (Test-Path "$PSScriptRoot\..\..\src_native\csharp\ZiPackCLI.exe")
        Win32Launcher = (Test-Path "$PSScriptRoot\..\..\zipack\bin\ZiPackLauncher.exe") -or (Test-Path "$PSScriptRoot\..\..\src_native\c\ZiPackLauncher.exe")
    }
}

function Compress-ZiPackArchive {
    <#
    .SYNOPSIS
    Compresses files or directories into a ZIP or 7z archive using ZiPack.
    .EXAMPLE
    Compress-ZiPackArchive -Source "C:\Docs" -Destination "C:\Backups\Docs.zip"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Source,

        [Parameter(Mandatory = $true, Position = 1)]
        [string]$Destination,

        [Parameter(Mandatory = $false)]
        [ValidateSet("Optimal", "Fastest", "NoCompression")]
        [string]$CompressionLevel = "Optimal"
    )

    if (-not (Test-Path $Source)) {
        Write-Error "Source path does not exist: $Source"
        return
    }

    $destDir = Split-Path -Parent (Resolve-Path -Path (Split-Path -Parent $Destination) -ErrorAction SilentlyContinue)
    if ($destDir -and -not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    # Prefer C# CLI if available for maximum speed
    $cliCandidates = @(
        "$PSScriptRoot\..\..\zipack\bin\ZiPackCLI.exe",
        "$PSScriptRoot\..\..\src_native\csharp\ZiPackCLI.exe"
    )
    $cliPath = $cliCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($cliPath) {
        Write-Verbose "Using ZiPack C# CLI accelerator..."
        & $cliPath compress $Destination $Source
        return
    }

    # Fallback to standard .NET Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    if (Test-Path $Destination) {
        Remove-Item $Destination -Force
    }

    if (Test-Path $Source -PathType Container) {
        [System.IO.Compression.ZipFile]::CreateFromDirectory($Source, $Destination, [System.IO.Compression.CompressionLevel]::$CompressionLevel, $false)
    } else {
        $zip = [System.IO.Compression.ZipFile]::Open($Destination, [System.IO.Compression.ZipArchiveMode]::Create)
        try {
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $Source, (Split-Path $Source -Leaf), [System.IO.Compression.CompressionLevel]::$CompressionLevel) | Out-Null
        } finally {
            $zip.Dispose()
        }
    }

    Write-Host "[ZiPack] Archive created: $Destination" -ForegroundColor Green
}

function Expand-ZiPackArchive {
    <#
    .SYNOPSIS
    Extracts an archive to a destination directory with Zip Slip security verification.
    .EXAMPLE
    Expand-ZiPackArchive -Path "archive.zip" -Destination "C:\Extracted"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Path,

        [Parameter(Mandatory = $false, Position = 1)]
        [string]$Destination
    )

    if (-not (Test-Path $Path)) {
        Write-Error "Archive file not found: $Path"
        return
    }

    if (-not $Destination) {
        $Destination = Join-Path (Split-Path -Parent (Resolve-Path $Path)) ([System.IO.Path]::GetFileNameWithoutExtension($Path))
    }

    if (-not (Test-Path $Destination)) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }

    # Prefer C# CLI
    $cliCandidates = @(
        "$PSScriptRoot\..\..\zipack\bin\ZiPackCLI.exe",
        "$PSScriptRoot\..\..\src_native\csharp\ZiPackCLI.exe"
    )
    $cliPath = $cliCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($cliPath) {
        Write-Verbose "Using ZiPack C# CLI accelerator..."
        & $cliPath extract $Path $Destination
        return
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($Path, $Destination)
    Write-Host "[ZiPack] Successfully extracted to $Destination" -ForegroundColor Green
}

function Test-ZiPackIntegrity {
    <#
    .SYNOPSIS
    Tests archive integrity and CRC32 streams.
    .EXAMPLE
    Test-ZiPackIntegrity -Path "archive.zip"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        Write-Error "Archive file not found: $Path"
        return
    }

    $cliCandidates = @(
        "$PSScriptRoot\..\..\zipack\bin\ZiPackCLI.exe",
        "$PSScriptRoot\..\..\src_native\csharp\ZiPackCLI.exe"
    )
    $cliPath = $cliCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($cliPath) {
        & $cliPath test $Path
        return
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    try {
        $zip = [System.IO.Compression.ZipFile]::OpenRead($Path)
        $buffer = New-Object byte[] 65536
        foreach ($entry in $zip.Entries) {
            $stream = $entry.Open()
            while ($stream.Read($buffer, 0, $buffer.Length) -gt 0) { }
            $stream.Dispose()
        }
        $zip.Dispose()
        Write-Host "[ZiPack] Archive integrity PASSED: $Path" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[ZiPack] Archive integrity FAILED: $_" -ForegroundColor Red
        return $false
    }
}

Export-ModuleMember -Function Get-ZiPackVersion, Compress-ZiPackArchive, Expand-ZiPackArchive, Test-ZiPackIntegrity

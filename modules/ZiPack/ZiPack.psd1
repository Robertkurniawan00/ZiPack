@{
    RootModule           = 'ZiPack.psm1'
    ModuleVersion        = '2.0.0'
    GUID                 = 'b7b2f4f2-9844-42b7-a352-7b1981e4b95f'
    Author               = 'ZiPack Studio'
    CompanyName          = 'ZiPack'
    Copyright            = '(c) 2026 ZiPack Studio. All rights reserved.'
    Description          = 'ZiPack PowerShell Automation Module for high-speed archive compression, extraction, and integrity checking.'
    PowerShellVersion    = '5.1'
    FunctionsToExport    = @('Get-ZiPackVersion', 'Compress-ZiPackArchive', 'Expand-ZiPackArchive', 'Test-ZiPackIntegrity')
    CmdletsToExport      = @()
    VariablesToExport    = @()
    AliasesToExport      = @()
    PrivateData          = @{
        PSData = @{
            Tags       = @('ZiPack', 'Archive', 'Compression', 'Zip', '7z', 'Fast')
            ProjectUri = 'https://github.com/Robertkurniawan00/ZiPack'
        }
    }
}

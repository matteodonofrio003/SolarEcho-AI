#requires -Version 5.1
<#
.SYNOPSIS
Invia il codice locale alla App SolarEcho su UNO Q via USB/ADB o SSH.
.EXAMPLE
.\deploy.ps1
.EXAMPLE
.\deploy.ps1 -Start
.EXAMPLE
.\deploy.ps1 -SshHost arduino@solarecho-unoq.local
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$AdbPath,
    [string]$Serial,
    [ValidatePattern('^(?:[A-Za-z0-9_-]+@)?[A-Za-z0-9][A-Za-z0-9.-]*$')]
    [string]$SshHost,
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_-]*$')]
    [string]$AppName = 'solarecho-ai',
    [switch]$Start
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$appRoot = Join-Path $PSScriptRoot 'app'
$remoteRoot = "/home/arduino/ArduinoApps/$AppName"
$files = @(
    'app.yaml', 'sketch/sketch.yaml', 'sketch/sketch.ino', 'sketch/ina219_monitor.h',
    'python/main.py', 'python/dashboard.py', 'python/power_history.py', 'python/electrical_demo.py',
    'python/inspection_alert.py',
    'assets/index.html', 'assets/style.css', 'assets/dashboard.js'
)

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    $lines = & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        if ($lines) { Write-Host ($lines -join "`n") }
        throw "Comando fallito ($LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
    return ($lines -join "`n")
}

foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath (Join-Path $appRoot $file) -PathType Leaf)) {
        throw "File locale mancante: app/$file"
    }
}

if ($SshHost) {
    $sshExecutable = (Get-Command ssh -ErrorAction Stop).Source
    $scpExecutable = (Get-Command scp -ErrorAction Stop).Source
} else {
    if (-not $AdbPath) {
        $adbCommand = Get-Command adb -ErrorAction SilentlyContinue
        if ($adbCommand) { $AdbPath = $adbCommand.Source }
    }
    if (-not $AdbPath) {
        $AdbPath = Get-Process adb -ErrorAction SilentlyContinue |
            Where-Object { $_.Path } | Select-Object -First 1 -ExpandProperty Path
    }
    if (-not $AdbPath) {
        $adbDirectory = Join-Path $env:LOCALAPPDATA 'Arduino15\packages\arduino\tools\adb'
        $AdbPath = Get-ChildItem -LiteralPath $adbDirectory -Filter adb.exe -Recurse -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
    }
    if (-not $AdbPath -or -not (Test-Path -LiteralPath $AdbPath -PathType Leaf)) {
        throw 'ADB non trovato. Aprire App Lab oppure usare -AdbPath con il percorso di adb.exe.'
    }

    $devices = Invoke-Checked $AdbPath @('devices')
    $connected = @($devices -split "`n" | ForEach-Object {
        if ($_ -match '^([^\s]+)\s+device\s*$') { $Matches[1] }
    })
    if ($Serial) {
        if ($Serial -notin $connected) { throw "Dispositivo USB $Serial non disponibile/autorizzato." }
    } elseif ($connected.Count -eq 1) {
        $Serial = $connected[0]
    } else {
        throw "Trovati $($connected.Count) dispositivi USB. Collegare UNO Q o specificare -Serial."
    }
}

function Invoke-Board {
    param([string]$Command)
    if ($SshHost) {
        Invoke-Checked $sshExecutable @('-o', 'ConnectTimeout=10', $SshHost, $Command)
    } else {
        Invoke-Checked $AdbPath @('-s', $Serial, 'shell', $Command)
    }
}

# Lo stato si legge prima di mutare file. Il CLI usa ID codificati nelle risposte JSON.
$listing = Invoke-Board 'arduino-app-cli app list --format json' | ConvertFrom-Json
$appId = "user:$AppName"
$encodedId = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($appId)).TrimEnd('=').Replace('+', '-').Replace('/', '_')
$targetApp = @($listing.apps | Where-Object { $_.id -eq $encodedId -or $_.id -eq $appId })
$activeOthers = @($listing.apps | Where-Object {
    $_.id -ne $encodedId -and $_.id -ne $appId -and $_.status -notin @('stopped', 'uninitialized')
})
if ($Start -and $activeOthers.Count -gt 0) {
    throw 'Un''altra App e attiva. Fermarla in App Lab prima di usare -Start.'
}

Write-Host "Destinazione: $remoteRoot"
if (-not $PSCmdlet.ShouldProcess($remoteRoot, 'Backup dei sorgenti, trasferimento e verifica SHA256')) {
    return
}
if ($targetApp.Count -gt 0 -and $targetApp[0].status -notin @('stopped', 'uninitialized')) {
    Write-Host 'Arresto SolarEcho prima del trasferimento...'
    Invoke-Board "arduino-app-cli app stop '$appId'" | Write-Host
}

$deployId = (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$backupRoot = "$remoteRoot/.deploy-backups/$deployId"
Invoke-Board "mkdir -p '$remoteRoot/sketch' '$remoteRoot/python' '$remoteRoot/assets' '$backupRoot/sketch' '$backupRoot/python' '$backupRoot/assets'" | Out-Null

foreach ($file in $files) {
    $localFile = Join-Path $appRoot $file
    $destination = "$remoteRoot/$file"
    $temporary = "$destination.deploy-$deployId"
    Invoke-Board "if [ -f '$destination' ]; then cp -- '$destination' '$backupRoot/$file'; fi" | Out-Null
    Write-Host "Invio app/$file"
    if ($SshHost) {
        Invoke-Checked $scpExecutable @('-o', 'ConnectTimeout=10', $localFile, "${SshHost}:$temporary") | Out-Null
    } else {
        Invoke-Checked $AdbPath @('-s', $Serial, 'push', $localFile, $temporary) | Out-Null
    }
    $localHash = (Get-FileHash -LiteralPath $localFile -Algorithm SHA256).Hash.ToLowerInvariant()
    $remoteHash = ((Invoke-Board "sha256sum '$temporary'") -split '\s+')[0]
    if ($localHash -ne $remoteHash) {
        throw "Checksum diverso per $file. Deploy interrotto; App non avviata."
    }
    Invoke-Board "mv -- '$temporary' '$destination'" | Out-Null
}

Write-Host "Deploy completato e verificato. Backup: $backupRoot"
if ($Start) {
    Write-Host 'Compilazione e avvio SolarEcho...'
    Invoke-Board "arduino-app-cli app start '$appId'" | Write-Host
} else {
    Write-Host 'Riaprire SolarEcho-AI in App Lab per ricaricare i file, poi premere Run.'
}

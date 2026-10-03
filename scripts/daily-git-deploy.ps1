param(
    [string]$Branch = "main",
    [switch]$DryRun,
    [string[]]$Paths
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LogDirectory = Join-Path $env:LOCALAPPDATA "SmartUrl\deploy-logs"
$LogPath = Join-Path $LogDirectory ("deploy-{0}.log" -f (Get-Date -Format "yyyyMMdd"))
$Status = "FAILED"

New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null

function Write-Log {
    param([string]$Message)
    Add-Content -LiteralPath $LogPath -Value ("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss K"), $Message)
}

function Invoke-Git {
    param([string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = @(& git -C $RepoRoot @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($exitCode -ne 0) {
        throw ("git {0} failed with exit code {1}" -f $Arguments[0], $exitCode)
    }
    return ($output | ForEach-Object { [string]$_ }) -join "`n"
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git is not available in PATH."
    }

    $currentBranch = (Invoke-Git -Arguments @("branch", "--show-current")).Trim()
    if ($currentBranch -ne $Branch) {
        throw ("Expected branch '{0}', found '{1}'. No files were pushed." -f $Branch, $currentBranch)
    }

    $remoteUrl = (Invoke-Git -Arguments @("remote", "get-url", "origin")).Trim()
    if ($remoteUrl -match "^[a-zA-Z][a-zA-Z0-9+.-]*://[^/]*@") {
        throw "The origin URL contains embedded credentials. Remove them and use Git Credential Manager."
    }

    Invoke-Git -Arguments @("fetch", "--prune", "origin", $Branch) | Out-Null

    if ($DryRun) {
        $workingStatus = Invoke-Git -Arguments @("status", "--short")
        Write-Log "DRY RUN: remote fetch succeeded; no files were staged, committed, or pushed."
        if ($workingStatus) {
            Write-Log "Working tree changes are present and were left untouched."
        }
        $Status = "SUCCESS"
        return
    }

    if ($Paths -and $Paths.Count -gt 0) {
        Invoke-Git -Arguments (@("add", "--all", "--") + $Paths) | Out-Null
    }
    else {
        Invoke-Git -Arguments @("add", "--all") | Out-Null
    }
    $stagedFiles = (Invoke-Git -Arguments @("diff", "--cached", "--name-only")) -split "`n" | Where-Object { $_ }
    $sensitiveFiles = @($stagedFiles | Where-Object {
        ($_ -match "(^|/)\.env($|\.)" -and $_ -ne ".env.example") -or
        $_ -match "(^|/)(id_(rsa|ed25519)|credentials?)(\.|$)" -or
        $_ -match "\.(pem|p12|pfx|key)$" -or
        $_ -match "(^|/)secrets?\.json$"
    })
    if ($sensitiveFiles.Count -gt 0) {
        throw "A credential-like file is staged. No commit or push was made; inspect the local Git status."
    }

    if ($stagedFiles.Count -gt 0) {
        $stagedPatch = Invoke-Git -Arguments @("diff", "--cached", "--unified=0")
        $credentialPattern = '(?m)^(\+[^+].*(-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})|\+[^+].*(password|secret|token|api[_-]?key|security.?code)\s*[:=]\s*["''][^"'']{8,})'
        if ($stagedPatch -match $credentialPattern) {
            throw "A credential-like value was detected in staged changes. No commit or push was made."
        }

        Invoke-Git -Arguments @("diff", "--cached", "--check") | Out-Null
        $commitMessage = "chore: scheduled sync {0}" -f (Get-Date -Format "yyyy-MM-dd")
        Invoke-Git -Arguments @("commit", "-m", $commitMessage) | Out-Null
        Write-Log "Committed local tracked and non-ignored changes."
    }
    else {
        Write-Log "No local file changes to commit."
    }

    try {
        Invoke-Git -Arguments @("rebase", ("origin/{0}" -f $Branch)) | Out-Null
    }
    catch {
        try {
            Invoke-Git -Arguments @("rebase", "--abort") | Out-Null
        }
        catch {
        }
        throw "Remote changes could not be merged cleanly. Rebase was aborted; resolve conflicts locally before the next run."
    }

    $aheadCount = [int](Invoke-Git -Arguments @("rev-list", "--count", ("origin/{0}..{0}" -f $Branch))).Trim()
    if ($aheadCount -gt 0) {
        Invoke-Git -Arguments @("push", "origin", $Branch) | Out-Null
        Write-Log ("SUCCESS: pushed {0} commit(s) to origin/{1}." -f $aheadCount, $Branch)
    }
    else {
        Write-Log ("SUCCESS: origin/{0} is up to date; no push was needed." -f $Branch)
    }
    $Status = "SUCCESS"
}
catch {
    Write-Log ("FAILED: {0}" -f $_.Exception.Message)
}
finally {
    Write-Log ("Finished with status {0}." -f $Status)
}

if ($Status -ne "SUCCESS") {
    exit 1
}
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Branch = "main"
$DeployScript = Join-Path $PSScriptRoot "daily-git-deploy.ps1"
$TaskName = "SmartUrl-DailyGitDeploy"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not available in PATH. Install Git for Windows before registering the task."
}

$credentialHelper = (& git -C $RepoRoot config --get credential.helper 2>$null | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $credentialHelper -notmatch "manager") {
    throw "Git Credential Manager is not configured. Configure it with 'git config --global credential.helper manager' before registering. Do not put a token in this script or the remote URL."
}

$remoteUrl = (& git -C $RepoRoot remote get-url origin 2>$null | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $remoteUrl -match "^[a-zA-Z][a-zA-Z0-9+.-]*://[^/]*@") {
    throw "The origin remote is missing or contains embedded credentials. Configure a credential-free origin URL first."
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date).AddMinutes(2) -RandomDelay (New-TimeSpan -Hours 23)
$actionArgs = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}"' -f $DeployScript
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs -WorkingDirectory $RepoRoot
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Write-Output ("Registered {0} for {1}. It uses Git Credential Manager and runs only while that Windows account is logged in." -f $TaskName, $identity)
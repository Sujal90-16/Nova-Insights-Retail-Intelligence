$ErrorActionPreference = 'Stop'

Write-Host 'Nova Insights - publish repository to GitHub' -ForegroundColor Cyan
Write-Host 'First create an EMPTY repository on https://github.com/new named Nova-Insights-Retail-Intelligence.'
Write-Host 'Do not initialize it with a README, license, or .gitignore because this project already has those files.'
$repoUrl = Read-Host 'Paste your new GitHub repository URL (HTTPS or SSH)'
if ([string]::IsNullOrWhiteSpace($repoUrl)) { throw 'Repository URL cannot be empty.' }

$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0 -and $existing) {
    git remote set-url origin $repoUrl
} else {
    git remote add origin $repoUrl
}
git push -u origin main
Write-Host 'Push completed. Open the repository URL in your browser.' -ForegroundColor Green

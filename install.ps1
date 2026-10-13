# Install the interview-video-editor-resolve skill for AI coding assistants (Windows PowerShell)
#
# Usage:
#   .\install.ps1                          # Install globally for Antigravity & .agents
#   .\install.ps1 -Workspace C:\path\proj  # Install project-locally in <proj>\.agents\skills
param(
  [string]$Workspace = "",
  [switch]$AntigravityOnly = $false,
  [switch]$All = $false
)

$ErrorActionPreference = "Stop"
$SkillName = "interview-video-editor-resolve"
$Src = Join-Path $PSScriptRoot $SkillName

if (-not (Test-Path (Join-Path $Src "SKILL.md"))) {
  if (Test-Path (Join-Path $PSScriptRoot "SKILL.md")) {
    $Src = $PSScriptRoot
  } else {
    throw "SKILL.md not found in $Src"
  }
}

$TargetRoots = @()

if ($Workspace) {
  $TargetRoots += (Join-Path $Workspace ".agents\skills")
  $TargetRoots += (Join-Path $Workspace ".agent\skills")
} else {
  if ($AntigravityOnly) {
    $TargetRoots += (Join-Path $HOME ".gemini\antigravity\skills")
  } else {
    $TargetRoots += (Join-Path $HOME ".gemini\config\skills")
    $TargetRoots += (Join-Path $HOME ".gemini\antigravity\skills")
    $TargetRoots += (Join-Path $HOME ".agents\skills")
  }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Installing $SkillName" -ForegroundColor Cyan
Write-Host "Source: $Src"
Write-Host "=========================================================="

foreach ($DestRoot in $TargetRoots) {
  New-Item -ItemType Directory -Force -Path $DestRoot | Out-Null
  $TargetPath = Join-Path $DestRoot $SkillName

  if (Test-Path $TargetPath) {
    $Bak = "$TargetPath.bak-" + (Get-Date -Format "yyyyMMdd-HHmmss")
    Move-Item $TargetPath $Bak
    Write-Host "  [backup] Moved existing directory to $Bak" -ForegroundColor Yellow
  }

  Copy-Item -Recurse -Force -Path $Src -Destination $TargetPath
  Write-Host "  [ok] Installed to: $TargetPath" -ForegroundColor Green
}

Write-Host "----------------------------------------------------------"
Write-Host "Successfully installed $SkillName." -ForegroundColor Green
Write-Host "Next Steps:"
Write-Host "1. Ensure DaVinci Resolve is running and the 'davinci-resolve' MCP server is configured."
Write-Host "2. Restart your AI assistant session, then prompt:"
Write-Host "   'Use the interview-video-editor-resolve skill to edit footage in ./footage'"
Write-Host "=========================================================="

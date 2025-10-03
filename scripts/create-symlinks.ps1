#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Creates symlinks from the cape repository to a target directory.

.DESCRIPTION
    This script creates symbolic links from the cape repository to a target directory:
    - Agent files (.md): agents/claude-code -> .claude/agents, agents/opencode -> .opencode/agent
    - Hook files: hooks/claude-code -> .claude/hooks
    - Documentation: ai_docs -> ai_docs
    
    Creates parent directories automatically and replaces existing symlinks.
    Preserves existing regular directories and files.
    
    NOTE: Requires administrator privileges to create symbolic links on Windows.

.PARAMETER TargetDir
    The absolute path of the target directory where symlinks should be created.

.PARAMETER Force
    Skip confirmation prompts and automatically copy environment file example.

.EXAMPLE
    .\scripts\create-symlinks.ps1 "C:\path\to\target"
    
.EXAMPLE
    .\scripts\create-symlinks.ps1 "C:\path\to\target" -Force
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TargetDir,
    
    [switch]$Force
)

# Expand the target directory path to handle ~ and relative paths
if ($TargetDir.StartsWith('~')) {
    $TargetDir = $TargetDir.Replace('~', $env:USERPROFILE)
}
$TargetDir = [System.IO.Path]::GetFullPath($TargetDir)

# Function to run a batch of commands in a single elevated session
function Invoke-ElevatedBatch {
    param(
        [string[]]$Commands,
        [string[]]$Descriptions
    )
    
    if ($Commands.Length -eq 0) {
        return @()
    }
    
    Write-Host "Creating $($Commands.Length) symlinks with elevated privileges..." -ForegroundColor Yellow
    
    # Create a script block with all commands
    $scriptContent = @()
    $scriptContent += "# Symlink creation batch script"
    $scriptContent += ""
    
    for ($i = 0; $i -lt $Commands.Length; $i++) {
        $scriptContent += "try {"
        $scriptContent += "    $($Commands[$i])"
        $scriptContent += "    Write-Host '✓ $($Descriptions[$i])' -ForegroundColor Green"
        $scriptContent += "} catch {"
        $scriptContent += "    Write-Host '✗ $($Descriptions[$i]) failed: $_' -ForegroundColor Red"
        $scriptContent += "}"
    }
    $scriptText = $scriptContent -join "`n"
    
    # Save script to temp file
    $tempScript = [System.IO.Path]::GetTempFileName() + ".ps1"
    Set-Content -Path $tempScript -Value $scriptText -Encoding UTF8
    
    try {
        if ($Force) {
            $process = Start-Process -FilePath "pwsh" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "`"$tempScript`"" -Verb "RunAs" -Wait -PassThru -WindowStyle Normal
        } else {
            $choice = Read-Host "Proceed with elevation to create $($Commands.Length) symlinks? (y/N)"
            if (-not ($choice -match '^[Yy]')) {
                Write-Host "Operation cancelled." -ForegroundColor Yellow
                Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
                return @()
            }
            $process = Start-Process -FilePath "pwsh" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", "`"$tempScript`"" -Verb "RunAs" -Wait -PassThru
        }
        
        # Return results based on exit code
        $success = $process.ExitCode -eq 0
        return @(1..$Commands.Length | ForEach-Object { $success })
    } catch {
        Write-Host "Batch execution failed: $_" -ForegroundColor Red
        return @()
    } finally {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}

# Ensure we're running from the repository root
$repoRoot = Split-Path -Parent $PSScriptRoot
# Verify this is the cape repository by checking for expected directories
if (-not ((Test-Path (Join-Path $repoRoot "agents")) -and (Test-Path (Join-Path $repoRoot "hooks")) -and (Test-Path (Join-Path $repoRoot "scripts")))) {
    Write-Error "This script must be run from the root of the cape repository (missing agents, hooks, or scripts directories)"
    exit 1
}

# Validate target directory path
if (-not [System.IO.Path]::IsPathRooted($TargetDir)) {
    Write-Error "Target directory must be an absolute path"
    exit 1
}

Write-Host "Repository root: $repoRoot"
Write-Host "Target directory: $TargetDir"
Write-Host ""

# Function to prepare symlink command for batch execution
function Add-SymlinkToBatch {
    param(
        [string]$Source,
        [string]$Target,
        [string]$Description,
        [ref]$Commands,
        [ref]$Descriptions
    )
    
    $sourceFullPath = Join-Path $repoRoot $Source
    $targetFullPath = Join-Path $TargetDir $Target
    
    # Check if source exists
    if (-not (Test-Path $sourceFullPath)) {
        Write-Warning "Source does not exist: $sourceFullPath"
        return $false
    }
    
    # Create parent directory for target if it doesn't exist
    $targetParent = Split-Path -Parent $targetFullPath
    if (-not (Test-Path $targetParent)) {
        Write-Host "Creating parent directory: $targetParent"
        New-Item -ItemType Directory -Path $targetParent -Force > $null
    }
    
    # Handle existing target
    if (Test-Path $targetFullPath) {
        $item = Get-Item $targetFullPath -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            # It's a symlink, add removal command
            Write-Host "Will remove existing symlink: $targetFullPath"
            $Commands.Value += "Remove-Item -Path '$targetFullPath' -Force"
            $Descriptions.Value += "Remove existing symlink at $targetFullPath"
        } elseif ($item.PSIsContainer) {
            # It's a directory, don't replace
            Write-Warning "Target directory already exists, skipping: $targetFullPath"
            return $false
        } else {
            # It's a file, don't replace
            Write-Warning "Target file already exists, skipping: $targetFullPath"
            return $false
        }
    }
    
    # Add the symlink creation command
    $Commands.Value += "New-Item -ItemType SymbolicLink -Path '$targetFullPath' -Value '$sourceFullPath' -Force > `$null"
    $Descriptions.Value += $Description
    
    return $true
}

Write-Host "Preparing symlink operations..."
Write-Host "============================="
Write-Host ""

# Collect all commands to run in batch
$commands = @()
$descriptions = @()

# Process agent files
Write-Host "Processing agent files..."
$agentDirs = @(
    @{ Source = "agents\claude-code"; Target = ".claude\agents" },
    @{ Source = "agents\opencode"; Target = ".opencode\agent" }
)

foreach ($agentDir in $agentDirs) {
    $sourceDir = Join-Path $repoRoot $agentDir.Source
    if (Test-Path $sourceDir) {
        $agentFiles = Get-ChildItem -Path $sourceDir -Filter "*.md" -File -ErrorAction SilentlyContinue
        foreach ($file in $agentFiles) {
            $sourcePath = "$($agentDir.Source)\$($file.Name)"
            $targetPath = "$($agentDir.Target)\$($file.Name)"
            $description = "Agent: $($file.Name)"
            $null = Add-SymlinkToBatch -Source $sourcePath -Target $targetPath -Description $description -Commands ([ref]$commands) -Descriptions ([ref]$descriptions)
        }
    } else {
        Write-Warning "Source directory not found: $sourceDir"
    }
}

# Process Claude Code hooks
Write-Host "Processing Claude Code hooks..."
$hooksPath = Join-Path $repoRoot "hooks\claude-code"
if (Test-Path $hooksPath) {
    $hooksItems = Get-ChildItem -Path $hooksPath -Force
    foreach ($item in $hooksItems) {
        $sourcePath = "hooks\claude-code\$($item.Name)"
        $targetPath = ".claude\hooks\$($item.Name)"
        $description = "Hook: $($item.Name)"
        $null = Add-SymlinkToBatch -Source $sourcePath -Target $targetPath -Description $description -Commands ([ref]$commands) -Descriptions ([ref]$descriptions)
    }
} else {
    Write-Warning "Hooks directory not found: $hooksPath"
}

# Process AI documentation
Write-Host "Processing AI documentation..."
$aiDocsPath = Join-Path $repoRoot "ai_docs"
if (Test-Path $aiDocsPath) {
    $aiDocsFiles = Get-ChildItem -Path $aiDocsPath -Filter "*.md" -File -ErrorAction SilentlyContinue
    foreach ($file in $aiDocsFiles) {
        $sourcePath = "ai_docs\$($file.Name)"
        $targetPath = "ai_docs\$($file.Name)"
        $description = "AI docs: $($file.Name)"
        $null = Add-SymlinkToBatch -Source $sourcePath -Target $targetPath -Description $description -Commands ([ref]$commands) -Descriptions ([ref]$descriptions)
    }
} else {
    Write-Warning "AI docs directory not found: $aiDocsPath"
}

Write-Host ""
Write-Host "Collected $($commands.Length) operations to execute."
Write-Host ""

# Execute all commands in a single elevated session
if ($commands.Length -gt 0) {
    $results = Invoke-ElevatedBatch -Commands $commands -Descriptions $descriptions
    $successCount = ($results | Where-Object { $_ -eq $true }).Count
    
    Write-Host ""
    Write-Host "===================="
    Write-Host "Symlink creation complete!"
    Write-Host "Successfully executed: $successCount/$($commands.Length) operations" -ForegroundColor $(if ($successCount -eq $commands.Length) { 'Green' } else { 'Yellow' })
    
    # Check if we created any Claude Code hooks symlinks
    $claudeHooksCreated = $descriptions | Where-Object { $_ -like "Hook:*" }
    if ($claudeHooksCreated) {
        Write-Host ""
        Write-Host "📋 Important Note:" -ForegroundColor Cyan
        Write-Host "The Claude Code hooks require API keys to be set in environment variables." -ForegroundColor Yellow
        Write-Host "You'll need to configure API keys for services like Anthropic, OpenAI, etc." -ForegroundColor Yellow
        Write-Host ""
        
        if ($Force) {
            # In Force mode, automatically copy the sample
            $copySample = $true
            Write-Host "Automatically copying environment variables example..." -ForegroundColor Green
        } else {
            # Ask user if they want to copy the sample
            $choice = Read-Host "Would you like to copy an example of the required environment variables? (Y/n)"
            $copySample = ($choice -eq "" -or $choice -match '^[Yy]')
        }
        
        if ($copySample) {
            $sampleFile = Join-Path $repoRoot ".env.hooks.example"
            $targetEnvFile = Join-Path $TargetDir ".env.hooks.example"
            
            if (Test-Path $sampleFile) {
                try {
                    Copy-Item -Path $sampleFile -Destination $targetEnvFile -Force
                    Write-Host "✓ Copied environment variables example to: .env.hooks.example" -ForegroundColor Green
                    Write-Host "  Edit this file and set your actual API keys as needed." -ForegroundColor Cyan
                } catch {
                    Write-Host "✗ Failed to copy environment variables example: $_" -ForegroundColor Red
                }
            } else {
                Write-Host "✗ Environment sample file not found at: $sampleFile" -ForegroundColor Red
            }
        } else {
            Write-Host "Skipped copying environment variables example." -ForegroundColor Yellow
            Write-Host "You can manually copy .env.example from this repository if needed later." -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "No symlink operations needed." -ForegroundColor Green
}

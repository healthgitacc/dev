# Script to push hospital project to dev branch

cd "e:\project\hospital"

# Check current status
Write-Host "Current Git Status:"
git status --short | Select-Object -First 5
Write-Host ""

# Add all changes
Write-Host "Staging all files..."
git add .
$stageCount = (git status --short | Measure-Object).Count
Write-Host "Total changes staged: $stageCount"
Write-Host ""

# Commit if there are changes
if ($stageCount -gt 0) {
    Write-Host "Creating commit..."
    git commit -m "Deploy: Hospital project - all files and folders at root level for dev branch"
    Write-Host ""
    Write-Host "Last commit:"
    git log --oneline -1
    Write-Host ""
} else {
    Write-Host "No changes to commit"
    Write-Host ""
}

# Check branches
Write-Host "Current branch:"
git branch
Write-Host ""

# Push to dev branch
Write-Host "Pushing to dev branch..."
git push -u origin dev
Write-Host ""
Write-Host "✓ Push completed!"

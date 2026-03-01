#!/usr/bin/env python3
"""
Simple script to push hospital project to GitHub
"""
import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a shell command and return output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, cwd="e:\\project\\hospital", 
                              capture_output=True, text=True,  timeout=60)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        if result.returncode != 0:
            print(f"Error: Command failed with return code {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    os.chdir("e:\\project\\hospital")
    
    # 1. Check git status
    run_command("git status", "Check current git status")
    
    # 2. Configure git if needed
    run_command('git config user.email "healthgitacc@example.com"', "Set git email")
    run_command('git config user.name "Health Git Account"', "Set git name")
    
    # 3. Add all files
    if run_command("git add .", "Stage all files"):
        print("✓ Files staged successfully")
    else:
        print("✗ Failed to stage files")
        return False
    
    # 4. Check what's staged
    run_command("git status -s | head -20", "Show first 20 staged files")
    
    # 5. Commit
    if run_command('git commit -m "feat: Push hospital project with dev folder organization"', "Create commit"):
        print("✓ Commit created successfully")
    else:
        print("✗ Failed to create commit")
        return False
    
    # 6. Push to GitHub
    if run_command("git push -u origin master", "Push to GitHub"):
        print("\n" + "="*60)
        print("✓ Successfully pushed to GitHub!")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("✗ Failed to push to GitHub")
        print("="*60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

import subprocess
import datetime
import os

def run_command(command):
    """Runs a shell command and prints the output."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        raise

def main():
    # Calculate timestamp for 12 hours ago
    now = datetime.datetime.now()
    twelve_hours_ago = now - datetime.timedelta(hours=12)
    date_str = twelve_hours_ago.strftime("%Y-%m-%d %H:%M:%S")

    print("--- Starting Git Automation ---")

    # Commit 1: Cleanup (12 hours ago)
    print(f"\nCreating Commit 1 (Timestamp: {date_str})...")
    try:
        # Stage deletions and .gitignore
        run_command("git add .gitignore")
        # git add -u stages modifications and deletions, but we want to be specific if possible.
        # Let's just stage the deleted files explicitly to be safe, or use 'git rm' if they are already deleted.
        # Since they are deleted in FS but not staged, 'git add -u' works well for them.
        # But we don't want to stage README or requirements yet if possible.
        # Let's try specific add.
        
        # Check if files exist before trying to rm them (they should be gone)
        # 'git add -u' will stage the deletions of missing files.
        # We want to stage ONLY deletions of ftest.py, chat_db.py, test_core_output.txt
        run_command("git add ftest.py chat_db.py test_core_output.txt") 
        
        # Commit with backdated timestamp
        run_command(f'git commit -m "Cleanup legacy files and restructure project" --date "{date_str}"')
    except Exception as e:
        print(f"Failed to create Commit 1: {e}")
        return

    # Commit 2: New Features (Now)
    print("\nCreating Commit 2 (Timestamp: Now)...")
    try:
        # Stage everything else (app.py, README.md, requirements.txt)
        run_command("git add .")
        run_command('git commit -m "Implement single-file architecture with app.py"')
    except Exception as e:
        print(f"Failed to create Commit 2: {e}")
        return

    # Push
    print("\nPushing to GitHub...")
    try:
        run_command("git push origin master") # Assuming master, change to main if needed
        print("Successfully pushed to GitHub!")
    except Exception as e:
        print(f"Failed to push: {e}")

if __name__ == "__main__":
    main()

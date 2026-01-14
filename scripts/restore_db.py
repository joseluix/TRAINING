import os
import subprocess
import sys
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to python executable in .venv
PYTHON_EXE = BASE_DIR / '.venv' / 'Scripts' / 'python.exe'
if not PYTHON_EXE.exists():
    PYTHON_EXE = 'python' # Fallback to system python

def run_restore(backup_file_path):
    backup_file = Path(backup_file_path)
    if not backup_file.exists():
        print(f"Error: Backup file not found: {backup_file}")
        return

    print(f"WARNING: This will load data into your current database.")
    print(f"It is recommended to run this on a fresh database after 'python manage.py migrate'.")
    confirm = input("Are you sure you want to proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Restore cancelled.")
        return

    command = [
        str(PYTHON_EXE),
        'manage.py',
        'loaddata',
        str(backup_file)
    ]

    print(f"Starting Django loaddata from {backup_file}...")
    
    try:
        result = subprocess.run(command, cwd=BASE_DIR, check=True, capture_output=True, text=True)
        print(f"Restore completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Restore failed!")
        print(f"Error output: {e.stderr}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python restore_db.py <path_to_backup_file>")
    else:
        run_restore(sys.argv[1])

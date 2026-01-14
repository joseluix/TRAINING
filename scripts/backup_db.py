import os
import subprocess
from datetime import datetime
from pathlib import Path

# Path configuration
BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / 'backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Path to python executable in .venv
PYTHON_EXE = BASE_DIR / '.venv' / 'Scripts' / 'python.exe'
if not PYTHON_EXE.exists():
    PYTHON_EXE = 'python' # Fallback to system python

def run_backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"db_backup_{timestamp}.json"

    # We exclude contenttypes and auth.permission because they are auto-generated
    # and can cause conflicts during loaddata if the DB is not completely empty.
    command = [
        str(PYTHON_EXE),
        'manage.py',
        'dumpdata',
        '--natural-foreign',
        '--natural-primary',
        '-e', 'contenttypes',
        '-e', 'auth.permission',
        '--indent', '2',
        '-o', str(backup_file)
    ]

    print(f"Starting Django dumpdata to {backup_file}...")
    
    try:
        result = subprocess.run(command, cwd=BASE_DIR, check=True, capture_output=True, text=True)
        print(f"Backup completed successfully: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Backup failed!")
        print(f"Error output: {e.stderr}")

if __name__ == '__main__':
    run_backup()

# Project Recovery and Migration Guide

This guide outlines how to restore this project on a new machine.

## 1. Local Database (SQLite)
The project is currently configured to use **SQLite** for ease of development and portability.
- Default database file: `db.sqlite3`
- Settings: `trading_web/settings.py`

## 2. Backup and Restore Scripts
Two Python scripts are provided in the `scripts/` directory to handle database data:

- **`backup_db.py`**: Creates a JSON snapshot of the database content.
- **`restore_db.py`**: Loads data from a JSON snapshot back into the database.

## 3. Migration Steps (To New PC/macOS)

### On Current Machine:
1. Run the backup script:
   ```bash
   python scripts/backup_db.py
   ```
2. Save the generated `.json` file from the `backups/` folder.

### On New Machine:
1. Clone the repository.
2. Set up your virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # or source .venv/bin/activate # macOS
   pip install -r requirements.txt
   ```
3. Initialize the database schema:
   ```bash
   python manage.py migrate
   ```
4. Restore your data:
   ```bash
   python scripts/restore_db.py <path_to_your_backup_file.json>
   ```
5. Create a new superuser (if not restored):
   ```bash
   python manage.py createsuperuser
   ```

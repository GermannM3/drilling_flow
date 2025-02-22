from datetime import datetime
import subprocess
from pathlib import Path
from app.core.config import settings

BACKUP_DIR = Path("/backups")

def create_db_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"backup_{timestamp}.sql"
    
    cmd = [
        "pg_dump",
        f"--dbname=postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}",
        f"--file={backup_file}",
        "--format=custom",
        "--compress=9"
    ]
    
    subprocess.run(cmd, check=True)
    
    # Удаляем старые бэкапы (оставляем последние 7)
    backups = sorted(BACKUP_DIR.glob("backup_*.sql"))
    for backup in backups[:-7]:
        backup.unlink()

# Добавим задачу в Celery
@celery.task
def scheduled_backup():
    create_db_backup() 
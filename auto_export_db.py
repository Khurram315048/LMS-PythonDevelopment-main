import subprocess
import time
import os
from datetime import datetime


DB_HOST     = '172.25.0.7'
DB_PORT     = '3306'
DB_USER     = 'root'
DB_PASSWORD = 'root'         
DB_NAME     = 'lms_db'       
OUTPUT_FILE = 'updated_lms.sql'  
CHECK_EVERY = 10    
MYSQLDUMP_PATH = '/usr/bin/mysqldump'   


def export_database():
    
    if DB_PASSWORD:
        command = [
            MYSQLDUMP_PATH,
            f'--host={DB_HOST}',
            f'--port={DB_PORT}',
            '--protocol=tcp',
            f'--user={DB_USER}',
            f'--password={DB_PASSWORD}',
            '--routines',
            '--triggers',
            '--single-transaction',
            DB_NAME
        ]
    else:
        command = [
            MYSQLDUMP_PATH,
            f'--host={DB_HOST}',
            f'--port={DB_PORT}',
            '--protocol=tcp',
            f'--user={DB_USER}',
            '--routines',
            '--triggers',
            '--single-transaction',
            DB_NAME
        ]

    try:
        with open(OUTPUT_FILE, 'w') as f:
            subprocess.run(command, stdout=f, stderr=subprocess.PIPE, check=True)
        now = datetime.now().strftime('%H:%M:%S')
        print(f"[{now}] ✅ Database exported to {OUTPUT_FILE}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Export failed: {e.stderr.decode()}")
        return False


def get_db_last_modified():
   
    try:
        import MySQLdb
        conn = MySQLdb.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            passwd=DB_PASSWORD,
            db='information_schema'
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(UPDATE_TIME) 
            FROM TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (DB_NAME,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return str(result[0]) if result and result[0] else None
    except Exception as e:
        print(f"⚠️ Could not check DB modification time: {e}")
        return None


print("🚀 Auto DB Export started. Watching for changes...")
print(f"   Database : {DB_NAME}")
print(f"   Output   : {OUTPUT_FILE}")
print(f"   Checking every {CHECK_EVERY} seconds")
print("   Press Ctrl+C to stop\n")


export_database()
last_known_time = get_db_last_modified()

while True:
    time.sleep(CHECK_EVERY)
    current_time = get_db_last_modified()

    if current_time != last_known_time:
        print(f"🔄 Change detected! Exporting...")
        if export_database():
            last_known_time = current_time
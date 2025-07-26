#!/usr/bin/env python3
# fix_sqlite_migration.py - Fix migration history in SQLite database

import sqlite3
from datetime import datetime

def fix_migration_history():
    """Fix the migration history by marking nr12_checklist.0001_initial as applied"""
    print("FIXING MIGRATION HISTORY IN SQLITE")
    print("=" * 50)
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if the migration record already exists
        cursor.execute("""
            SELECT COUNT(*) FROM django_migrations 
            WHERE app = 'nr12_checklist' AND name = '0001_initial';
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            print("Migration nr12_checklist.0001_initial already exists in database")
        else:
            # Insert the migration record
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('nr12_checklist', '0001_initial', ?);
            """, (current_time,))
            conn.commit()
            print("Added nr12_checklist.0001_initial to migration history")
        
        # Show current migration status
        cursor.execute("""
            SELECT app, name, applied FROM django_migrations 
            WHERE app IN ('nr12_checklist', 'equipamentos') 
            ORDER BY app, name;
        """)
        
        print("\nCurrent migration status:")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  {row[0]}.{row[1]} - {row[2]}")
            
        conn.close()
        
        print("\n" + "=" * 50)
        print("MIGRATION HISTORY FIXED!")
        print("\nNow you can run:")
        print("  python manage.py migrate")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_migration_history()
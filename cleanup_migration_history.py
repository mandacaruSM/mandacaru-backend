#!/usr/bin/env python3
# cleanup_migration_history.py - Clean up migration history to match file system

import sqlite3
from datetime import datetime

def cleanup_migration_history():
    """Clean up migration history to match current file system"""
    print("CLEANING UP MIGRATION HISTORY")
    print("=" * 50)
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Show current nr12_checklist migrations in database
        cursor.execute("""
            SELECT name FROM django_migrations 
            WHERE app = 'nr12_checklist' 
            ORDER BY name;
        """)
        db_migrations = [row[0] for row in cursor.fetchall()]
        print("Current nr12_checklist migrations in database:")
        for migration in db_migrations:
            print(f"  - {migration}")
        
        # File system only has 0001_initial.py
        file_migrations = ['0001_initial']
        print(f"\nMigrations in file system:")
        for migration in file_migrations:
            print(f"  - {migration}")
        
        # Remove migrations that don't exist in file system
        migrations_to_remove = [m for m in db_migrations if m not in file_migrations]
        
        if migrations_to_remove:
            print(f"\nRemoving migrations that don't exist in file system:")
            for migration in migrations_to_remove:
                print(f"  - Removing {migration}")
                cursor.execute("""
                    DELETE FROM django_migrations 
                    WHERE app = 'nr12_checklist' AND name = ?;
                """, (migration,))
            
            conn.commit()
            print(f"\nRemoved {len(migrations_to_remove)} migration records")
        else:
            print("\nNo cleanup needed - database matches file system")
        
        # Show final status
        cursor.execute("""
            SELECT app, name, applied FROM django_migrations 
            WHERE app IN ('nr12_checklist', 'equipamentos') 
            ORDER BY app, name;
        """)
        
        print("\nFinal migration status:")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  {row[0]}.{row[1]} - {row[2]}")
            
        conn.close()
        
        print("\n" + "=" * 50)
        print("MIGRATION HISTORY CLEANED UP!")
        print("\nNow you can run:")
        print("  python manage.py makemigrations nr12_checklist")
        print("  python manage.py migrate")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    cleanup_migration_history()
#!/usr/bin/env python3
# test_migrations.py - Test if migrations work now

import sqlite3

def test_migrations():
    """Test if the migration dependency issue is resolved"""
    print("TESTING MIGRATION DEPENDENCIES")
    print("=" * 50)
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if the dependency is satisfied
        cursor.execute("""
            SELECT app, name, applied FROM django_migrations 
            WHERE (app = 'nr12_checklist' AND name = '0001_initial')
               OR (app = 'equipamentos' AND name = '0005_equipamento_tipo_nr12_equipamento_updated_at_and_more')
            ORDER BY applied;
        """)
        
        rows = cursor.fetchall()
        
        if len(rows) == 2:
            nr12_migration = rows[0] if rows[0][0] == 'nr12_checklist' else rows[1]
            equipamentos_migration = rows[1] if rows[1][0] == 'equipamentos' else rows[0]
            
            print("Migration dependency check:")
            print(f"  nr12_checklist.0001_initial: {nr12_migration[2]}")
            print(f"  equipamentos.0005_...: {equipamentos_migration[2]}")
            
            # Check if nr12_checklist was applied before equipamentos
            if nr12_migration[2] < equipamentos_migration[2]:
                print("\n✅ DEPENDENCY SATISFIED!")
                print("   nr12_checklist.0001_initial was applied BEFORE equipamentos.0005")
                print("   The migration dependency issue is RESOLVED!")
                
                # Check if the TipoEquipamentoNR12 table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='nr12_checklist_tipoequipamentonr12';
                """)
                
                if cursor.fetchone():
                    print("   TipoEquipamentoNR12 table exists in database")
                else:
                    print("   ⚠️  TipoEquipamentoNR12 table not found - may need to run migrate")
                
                result = True
            else:
                print("\n❌ DEPENDENCY NOT SATISFIED!")
                print("   equipamentos migration was applied before nr12_checklist")
                result = False
        else:
            print("❌ Could not find both required migrations")
            result = False
        
        conn.close()
        
        print("\n" + "=" * 50)
        if result:
            print("✅ MIGRATION TEST PASSED!")
            print("\nThe dependency issue has been resolved.")
            print("You should now be able to run:")
            print("  python manage.py makemigrations nr12_checklist")
            print("  python manage.py migrate")
        else:
            print("❌ MIGRATION TEST FAILED!")
            print("Further investigation needed.")
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_migrations()
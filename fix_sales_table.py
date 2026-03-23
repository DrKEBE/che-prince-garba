import sqlite3

# Chemin vers ta base de données SQLite
db_path = r"C:\Users\DrKEBE\CodeKeb\che-prince-garba\backend\che_prince_garba.db"

# Connexion à la base
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vérifier si la colonne existe déjà pour éviter une erreur
cursor.execute("PRAGMA table_info(sales);")
columns = [col[1] for col in cursor.fetchall()]

if "total_profit" not in columns:
    cursor.execute("ALTER TABLE sales ADD COLUMN total_profit REAL DEFAULT 0;")
    print("✅ Colonne 'total_profit' ajoutée avec succès !")
else:
    print("ℹ️ La colonne 'total_profit' existe déjà.")

# Valider et fermer
conn.commit()
conn.close()

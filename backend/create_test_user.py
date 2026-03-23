# create_test_user.py
from database import SessionLocal
from models import User
from routes.auth import get_password_hash

db = SessionLocal()
# Vérifier si l'utilisateur admin existe déjà
admin = db.query(User).filter(User.username == "admin").first()
if not admin:
    hashed = get_password_hash("admin123")
    user = User(
        username="admin",
        email="admin@example.com",
        full_name="Administrateur",
        hashed_password=hashed,
        role="ADMIN",
        is_active=True
    )
    db.add(user)
    db.commit()
    print("✅ Utilisateur admin créé (mdp: admin123)")
else:
    print("ℹ️ L'utilisateur admin existe déjà")
db.close()
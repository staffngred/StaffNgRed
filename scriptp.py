from app import create_app, db
from app.models import User, Routine  # ajuste en fonction de tes modèles
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    # Vérifie si l'admin existe déjà
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            password=generate_password_hash("Abz1Qxt@"), 
            is_admin=True,
            is_approved=True,
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Compte admin créé : admin / admin123")
    else:
        print("ℹ️ Le compte admin existe déjà.")

    print("✅ Base de données initialisée avec succès.")

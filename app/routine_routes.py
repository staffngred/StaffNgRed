from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import db, Routine
from datetime import datetime, timedelta
from pytz import utc
routine_bp = Blueprint("routine", __name__)
from app.models import Rapport

def user_can_access():
    return current_user.is_authenticated and current_user.role in ("admin", "modérateur+")


@routine_bp.route("/routine")
@login_required
def routine_page():
    print(f"DEBUG current_user.role: '{current_user.role}'")

    if not user_can_access():
        flash("Accès refusé.")
        print("DEBUG Accès refusé, redirection vers profile")
        return redirect(url_for("main.profile"))

    print("DEBUG Accès autorisé, affichage de routine")

    try:
        routines = Routine.query.order_by(Routine.start_time.desc()).all()
        last_routine = Routine.query.order_by(Routine.start_time.desc()).first()
        now = datetime.utcnow()
        can_add = True
        if last_routine and last_routine.start_time + timedelta(minutes=90) > now:
            can_add = False

        return render_template("routine.html", routines=routines, can_add=can_add)

    except Exception as e:
        print("❌ Erreur dans routine_page :", e)
        return "Erreur interne", 500

@routine_bp.route("/routine/start", methods=["POST"])
@login_required
def start_routine():
    if not user_can_access():
        return jsonify({"error": "Accès refusé."}), 403

    last_routine = Routine.query.order_by(Routine.start_time.desc()).first()
    now = datetime.utcnow()

    if last_routine and last_routine.start_time + timedelta(minutes=90) > now:
        return jsonify({"error": "Une routine a déjà été lancée il y a moins d'une seconde."}), 400

    routine = Routine(
        start_time=now,
        created_by_id=current_user.id
    )
    db.session.add(routine)
    db.session.commit()

    return jsonify({"success": "Routine lancée."})


from flask_login import current_user
from app.models import Routine, Rapport

@routine_bp.route('/routine/<int:routine_id>/finish', methods=['POST'])
@login_required
def finish_routine(routine_id):
    data = request.get_json()
    comment = data.get('comment', '').strip()

    routine = Routine.query.get_or_404(routine_id)
    if routine.end_time:
        return jsonify({'error': 'Routine déjà terminée.'}), 400

    routine.end_time = datetime.utcnow()

    # Si "RAS", on enregistre juste dans la description
    if comment.upper() == 'RAS':
        routine.description = "RAS"
    elif comment:  # Si autre chose que vide
        # Crée un rapport
        rapport = Rapport(
            routine_id=routine.id,
            contenu=comment,
            created_by_id=current_user.id
        )
        db.session.add(rapport)

    db.session.commit()
    return jsonify({'success': True})




@routine_bp.route("/routine/mark_cheater/<int:routine_id>", methods=["POST"])
@login_required
def mark_cheater(routine_id):
    if not user_can_access():
        return jsonify({"error": "Accès refusé."}), 403
    routine = Routine.query.get_or_404(routine_id)
    cheater_name = request.json.get("cheater", "").strip()
    if cheater_name:
        routine.cheater = cheater_name
        routine.resolved = False
        db.session.commit()
        return jsonify({"success": "Tricheur marqué."})
    return jsonify({"error": "Nom de tricheur requis."}), 400

@routine_bp.route("/routine/resolve/<int:routine_id>", methods=["POST"])
@login_required
def resolve_issue(routine_id):
    if not user_can_access():
        return jsonify({"error": "Accès refusé."}), 403
    routine = Routine.query.get_or_404(routine_id)
    routine.resolved = True
    db.session.commit()
    return jsonify({"success": "Problème résolu."})


from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

@routine_bp.route('/rapport/<int:rapport_id>/statut', methods=['POST'])
@login_required
def changer_statut_rapport(rapport_id):
    data = request.get_json()
    nouveau_statut = data.get('statut')

    rapport = Rapport.query.get_or_404(rapport_id)
    if nouveau_statut in ['fait', 'refuse', 'en_attente']:
        rapport.statut = nouveau_statut
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Statut invalide'}), 400
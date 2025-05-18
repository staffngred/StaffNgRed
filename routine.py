
from flask import Blueprint, request, jsonify, render_template, abort
from flask_login import current_user, login_required
from functools import wraps
from datetime import datetime, timedelta
from app import db
from app.models import User

bp = Blueprint('routine', __name__, url_prefix='/routine')

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    remarks = db.Column(db.Text, default="")
    has_issue = db.Column(db.Boolean, default=False)
    issue_resolved = db.Column(db.Boolean, default=False)
    reported_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_by = db.relationship('User', foreign_keys=[created_by_id])
    reported_by = db.relationship('User', foreign_keys=[reported_by_id])

    def is_active(self):
        return self.end_time is None

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_view
    return wrapper

@bp.route('/status')
@login_required
@roles_required('admin', 'modérateur+')
def get_status():
    active = Routine.query.filter_by(end_time=None).first()
    last_finished = Routine.query.filter(Routine.end_time.isnot(None)).order_by(Routine.end_time.desc()).first()

    can_start = True
    remaining = 0
    if last_finished:
        delta = datetime.utcnow() - last_finished.end_time
        if delta < timedelta(minutes=90):
            can_start = False
            remaining = (timedelta(minutes=90) - delta).total_seconds()

    data = {
        'active': {
            'id': active.id if active else None,
            'start_time': active.start_time.isoformat() if active else None,
            'remarks': active.remarks if active else '',
            'has_issue': active.has_issue if active else False,
            'issue_resolved': active.issue_resolved if active else False,
        } if active else None,
        'can_start': can_start,
        'remaining_seconds': int(remaining)
    }
    return jsonify(data)

@bp.route('/start', methods=['POST'])
@login_required
@roles_required('admin', 'modérateur+')
def start_routine():
    last_finished = Routine.query.filter(Routine.end_time.isnot(None)).order_by(Routine.end_time.desc()).first()
    if last_finished and (datetime.utcnow() - last_finished.end_time) < timedelta(minutes=90):
        return jsonify({'error': 'Attendez 1h30 entre deux routines'}), 400
    
    routine = Routine(created_by=current_user)
    db.session.add(routine)
    db.session.commit()
    return jsonify({'success': True, 'routine_id': routine.id})

@bp.route('/end/<int:routine_id>', methods=['POST'])
@login_required
@roles_required('admin', 'modérateur+')
def end_routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    if routine.end_time is not None:
        return jsonify({'error': 'Routine déjà terminée'}), 400
    
    remarks = request.json.get('remarks', '').strip()
    routine.end_time = datetime.utcnow()
    routine.remarks = remarks
    routine.has_issue = bool(remarks)
    routine.issue_resolved = False
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/resolve/<int:routine_id>', methods=['POST'])
@login_required
@roles_required('admin')
def resolve_issue(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    if not routine.has_issue or routine.issue_resolved:
        return jsonify({'error': 'Aucun problème à résoudre'}), 400
    routine.issue_resolved = True
    routine.reported_by = current_user
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/list')
@login_required
@roles_required('admin', 'modérateur+')
def list_routines():
    routines = Routine.query.order_by(Routine.start_time.desc()).limit(20).all()
    return render_template('routine_list.html', routines=routines)

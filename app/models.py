from datetime import datetime
from . import db, login_manager  # importe l'instance db et login_manager déjà créées dans __init__.py
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='utilisateur')

    # Relations vers Routine (on précise foreign_keys pour lever l'ambiguïté)
    routines_created = db.relationship('Routine', foreign_keys='Routine.created_by_id', backref='creator', lazy=True)
    routines_reported = db.relationship('Routine', foreign_keys='Routine.reported_by_id', backref='reporter', lazy=True)
    routines_user = db.relationship('Routine', foreign_keys='Routine.user_id', backref='user', lazy=True)

class Routine(db.Model):
    __tablename__ = 'routine'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    remarks = db.Column(db.Text, default="")
    has_issue = db.Column(db.Boolean, default=False)
    issue_resolved = db.Column(db.Boolean, default=False)

    reported_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    rapports = db.relationship('Rapport', back_populates='routine', cascade='all, delete-orphan')

    def is_active(self):
        return self.end_time is None

class Rapport(db.Model):
    __tablename__ = 'rapport'

    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'))
    contenu = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String, default='en attente')

    creator = db.relationship('User', foreign_keys=[created_by_id])
    routine = db.relationship('Routine', back_populates='rapports')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

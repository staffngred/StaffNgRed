from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from .models import User  # Assurez-vous d'importer votre modèle User pour la validation

# Formulaire de connexion
class LoginForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[InputRequired()])
    password = PasswordField('Mot de passe', validators=[InputRequired()])
    submit = SubmitField('Connexion')

# Formulaire d'inscription
class RegisterForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[InputRequired(), Length(min=4)])
    password = PasswordField('Mot de passe', validators=[InputRequired(), Length(min=6)])
    submit = SubmitField('Créer un compte')

    # Validation personnalisée pour vérifier l'unicité du nom d'utilisateur
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d’utilisateur est déjà pris.')

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Ancien mot de passe', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Changer le mot de passe')

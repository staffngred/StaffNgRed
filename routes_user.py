from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .forms import ChangePasswordForm
from . import db

user = Blueprint('user', __name__)

@user.route('/user/dashboard')
@login_required
def dashboard():
    if not current_user.is_approved:
        flash("Votre compte est en attente d'approbation. Certaines fonctionnalités sont restreintes.", "warning")
    return render_template('user_dashboard.html', user=current_user)

@user.route('/user/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.old_password.data):
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Mot de passe modifié avec succès.", "success")
            return redirect(url_for('user.dashboard'))
        else:
            flash("Ancien mot de passe incorrect.", "danger")
    return render_template('profile.html', form=form)

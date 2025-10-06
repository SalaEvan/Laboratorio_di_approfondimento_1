from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from models.connection import db
from models.model import User

app = Blueprint('auth', __name__)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('default.index'))
    return render_template('/auth/login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    
    stmt = db.select(User).filter_by(email=email)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user:
        if user.check_password(password):
            login_user(user)
            return redirect(url_for('default.index'))
        else:
            flash('Invalid password. Please try again.')
            return redirect(url_for('auth.login'))
    else:
        flash('Invalid account. Please try again.')
        return redirect(url_for('auth.login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('/auth/login.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('/auth/profile.html', name=current_user.username)


@app.route('/register', methods=['GET'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('auth.profile'))
    return render_template('/auth/register.html')


@app.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Username e password obbligatori')
        return redirect(url_for('auth.register'))

    if User.query.filter_by(username=username).first():
        flash('Username già esistente')
        return redirect(url_for('auth.register'))

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash('Registrazione completata, ora puoi accedere')
    return redirect(url_for('auth.login'))
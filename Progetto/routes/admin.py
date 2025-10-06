from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.connection import db
from models.model import User, StairCalculation

app = Blueprint('admin', __name__)


def is_admin() -> bool:
    return bool(getattr(current_user, 'role', None) == 'admin')


@app.route('/calculations')
@login_required
def calculations_dashboard():
    if not is_admin():
        return render_template('auth/login.html'), 403

    # Query del numero di calcoli per utente
    rows = (
        db.session.query(User.id, User.username, db.func.count(StairCalculation.id))
        .outerjoin(StairCalculation, StairCalculation.user_id == User.id)
        .group_by(User.id, User.username)
        .order_by(User.username.asc())
        .all()
    )
    user_counts = [
        {"user_id": uid, "username": uname, "count": count}
        for uid, uname, count in rows
    ]
    return render_template('admin/calculations.html', user_counts=user_counts)
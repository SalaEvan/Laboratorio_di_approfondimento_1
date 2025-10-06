import datetime
from models.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128))
    role = db.Column(db.String(32), default='user', nullable=False)

    # self nel metodo [ set_password(self, password): ] serve per dire al metodo ceh fa parte della classe User
    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return check_password_hash(self.password_hash, password)

    # __repr__ dice a Python come rappresentare un oggetto in forma testuale. -->
    def __repr__(self):
        return f'<User id:{self.id} username:{self.username}>'
    
    def to_dict(self):
        data = {
            'id':self.id,
            'username':self.username,
            'role': self.role
        }
        return data
    


class StairCalculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_height = db.Column(db.Float, nullable=False)
    total_length = db.Column(db.Float, nullable=False)
    num_steps = db.Column(db.Integer, nullable=False)
    riser_height = db.Column(db.Float, nullable=False)
    tread_length = db.Column(db.Float, nullable=False)
    overhang = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref='stair_calculations')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'total_height': self.total_height,
            'total_length': self.total_length,
            'num_steps': self.num_steps,
            'riser_height': self.riser_height,
            'tread_length': self.tread_length,
            'overhang': self.overhang,
        }


class AppConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    overhang_factor = db.Column(db.Float, nullable=False, default=0.16) 

from datetime import datetime
from random import choices
from typing import Dict
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

from src import bcrypt
from src.links.models import Link
from src.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    link = db.relationship('Link', backref='url', lazy=True)

    # def get_reset_token(self, expires_sec=1800):
    #     s = Serialzer(current_app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')

    def __repr__(self):
        return f"User('{self.username}, {self.email}, {self.id}, {self.created}')"

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # def json(self) -> Dict:
    #     return {
    #         "id": self.id,
    #         "username": self.username,
    #         "email": self.email,
    #         "created": self.created,
    #         # "link": self.link
    #     }

    @staticmethod
    def password_create():
        pw_gen = bcrypt.generate_password_hash('admin').decode('utf-8')
        return pw_gen

    @staticmethod
    def admin_user():
        if not User.query.filter(User.username == 'admin').first():
            # hashed_password = User.password_create('admin')
            hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
            user1 = User(username='admin', password=hashed_password, email='admin@lst.am')
            db.session.add(user1)
            db.session.commit()
        # else:
        #     print('user exists')

    @staticmethod
    def link_count(id):
        total_links = db.session.query(db.func.count()).filter(Link.user_id == id).scalar()
        return total_links





import string
from uuid import uuid1
from datetime import datetime
from random import choices
from flask_login import UserMixin, AnonymousUserMixin

from .extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'
    #     self.email = 'test@test.com'
    #
    #     print
    #     "Exec"
    #
    # def is_authenticated(self):
    #     # return True
    #     return False
    #
    # def is_active(self):
    #     return True
    #     # return False
    #
    # def is_anonymous(self):
    #     return True
    #
    # def get_id(self):
    #     return 1


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    link = db.relationship('Link', backref='url', lazy=True)

    # def get_reset_token(self, expires_sec=1800):
    #     s = Serialzer(current_app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')

    def __repr__(self):
        return f"User('{self.username}, {self.email}')"


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # id = db.Column(db.String, name="uuid", primary_key=True, default=uuid4().int)
    url_org = db.Column(db.String(512))
    url_short = db.Column(db.String(12), unique=True)
    clicks = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, url_short, **kwargs):
        super().__init__(**kwargs)
        self.url_short = url_short or self.generate_short_link()
        self.id = uuid1().fields[0]
        # self.url = self.url or anonymous
        # self.id = uuid1().int >> 64
        # self.user_id = self.user_id or "demo"

    def generate_short_link(self):
        characters = string.digits + string.ascii_letters
        url_short = ''.join(choices(characters, k=3))

        link = self.query.filter_by(url_short=url_short).first()

        if link:
            return self.generate_short_link()

        return url_short

    # def anonymous(AnonymousUserMixin):
    #     def __init__(self):
    #         self.username = 'Demo'

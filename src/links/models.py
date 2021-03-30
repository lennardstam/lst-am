import string
from uuid import uuid1
from datetime import datetime
from random import choices

from src.extensions import db   # login_manager


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

    # def count(self):
    #     links = self.query.filter_by(user_id=self.user_id).count()
    #     return links
    #     # link_vol = Link.query.filter_by(user_id=user.id).all()

    # def anonymous(AnonymousUserMixin):
    #     def __init__(self):
    #         self.username = 'Demo'

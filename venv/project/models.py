from flask_login import UserMixin
from . import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    email_me = db.Column(db.Boolean, default=False)
    email_date = db.Column(db.DateTime)
    def __repr__(self):
        return '<Todo %r>' % self.id


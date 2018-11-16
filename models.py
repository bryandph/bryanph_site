from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(256), unique=True)
    # passwordHash = db.Column(db.String(256))
    name = db.Column(db.String(256))
    approved = db.Column(db.Boolean)


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

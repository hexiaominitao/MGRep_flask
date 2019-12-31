from flask_sqlalchemy import SQLAlchemy
from flask_mongoengine import MongoEngine

db = SQLAlchemy()
mongo = MongoEngine()

from app.models.user import User, Role

User = User
Role = Role

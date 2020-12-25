from . import db

db.init_app(app=project)
db.create_all()
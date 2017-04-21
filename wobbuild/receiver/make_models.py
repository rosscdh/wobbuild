from models import db, Project, Build
db.connect()
db.create_tables([Project, Build])
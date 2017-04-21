#
# >>> from wobbuild.receiver.models import db,Project,Build
# >>> db.create_tables([Project,Build])
# p, is_new = Project.get_or_create(name='rwd-douglas-pattern')
#
import peewee as pw

db = pw.SqliteDatabase('wobbuild.db')


class Project(pw.Model):
    name = pw.CharField(255, unique=True, index=True)
    data = pw.TextField(null=True)

    class Meta:
        database = db


class Build(pw.Model):
    slug = pw.CharField(255, unique=True, index=True)
    project = pw.ForeignKeyField(Project, related_name='builds')
    dateof = pw.TimestampField(null=True)
    pipeline = pw.TextField(null=True)
    logs = pw.TextField(null=True)

    class Meta:
        database = db
        order_by = ['-dateof']

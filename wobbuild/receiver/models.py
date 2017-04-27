#
# >>> from wobbuild.receiver.models import db,Project,Build
# >>> db.create_tables([Project,Build])
# p, is_new = Project.get_or_create(name='rwd-douglas-pattern')
#
import os
import json
import peewee as pw
from wobbuild.settings import BASE_PATH

db = pw.SqliteDatabase(os.path.join(BASE_PATH, 'wobbuild.db'))


class JSONField(pw.TextField):
    def db_value(self, value):
        """Convert the python value for storage in the database."""
        return value if value is None else json.dumps(value)

    def python_value(self, value):
        """Convert the database value to a pythonic value."""
        return value if value is None else json.loads(value)


class Project(pw.Model):
    name = pw.CharField(255, unique=True, index=True)
    data = JSONField(null=True, default={})

    class Meta:
        database = db


class Build(pw.Model):
    slug = pw.CharField(255, unique=True, index=True)
    project = pw.ForeignKeyField(Project, related_name='builds')
    dateof = pw.TimestampField(null=True)
    pipeline = JSONField(null=True, default={})
    step_logs = JSONField(null=True, default={})
    status = pw.CharField(16, index=True)

    class Meta:
        database = db
        order_by = ['-dateof']

    @property
    def status_icon(self):
        if self.status == 'created':
            return 'plus-circle'
        if self.status == 'success':
            return 'check'
        if self.status == 'failure':
            return 'exclamation'
        if self.status == 'rejected':
            return 'eject'
        return 'question'


db.create_tables([Project, Build], safe=True)

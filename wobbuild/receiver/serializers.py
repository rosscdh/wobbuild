from flask import Flask

from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)


class ProjectSchema(ma.Schema):
    class Meta:
        fields = (
            'name',
        )


class BuildSchema(ma.Schema):
    project = ma.Nested(ProjectSchema)

    class Meta:
        # Fields to expose
        fields = (
            'slug',
            'project',
            'dateof',
            'pipeline',
            'step_logs',
            'status',
        )
    # Smart hyperlinking
    # _links = ma.Hyperlinks({
    #     'self': ma.URLFor('author_detail', id='<id>'),
    #     'collection': ma.URLFor('authors')
    # })

build_schema = BuildSchema()
builds_schema = BuildSchema(many=True)

from flask import Flask

from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)


class BuildSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = (
            'slug',
            #'project',
            'dateof',
            #'pipeline',
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

from flask_classy import FlaskView
from flask import Flask, request, jsonify, render_template

from flask_restful import Api

from wobbuild.app_logger import gelf_handler

from wobbuild.receiver.models import Build
from wobbuild.receiver.api import BuildList, BuildDetail
from wobbuild.receiver.serializers import builds_schema

from wobbuild.services import perform

app = Flask(__name__)
app.logger.addHandler(gelf_handler)
app.config['TEMPLATES_AUTO_RELOAD'] = True

api = Api(app)
api.add_resource(BuildList, '/api/builds')
api.add_resource(BuildDetail, '/api/builds/<string:slug>')


class ProjectsView(FlaskView):
    route_base = '/'

    def get(self):
        res = builds_schema.dump(Build.select().limit(25))
        return render_template('build_list.html',
                               object_list=res.data)

    def post(self):
        app.logger.info('Got POST pipeline_receiver', {'host': request.host, 'url': request.url, 'remote_addr': request.remote_addr})

        resp = perform(pipeline_yaml=request.data.decode('utf-8'))

        return jsonify({'message': 'Thanks', 'resp': resp})


ProjectsView.register(app)
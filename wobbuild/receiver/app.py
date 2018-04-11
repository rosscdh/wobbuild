from flask_classy import FlaskView
from flask import Flask, request, jsonify, render_template

from flask_restful import Api

from wobbuild.app_logger import gelf_handler

from wobbuild.receiver.models import Build, Project
from wobbuild.receiver.api import BuildList, BuildDetail, ProjectList, ProjectDetail
from wobbuild.receiver.serializers import builds_schema, projects_schema

from wobbuild.services import perform

app = Flask(__name__)
app.logger.addHandler(gelf_handler)
app.config['TEMPLATES_AUTO_RELOAD'] = True

api = Api(app)
api.add_resource(BuildList, '/api/builds')
api.add_resource(BuildDetail, '/api/builds/<string:slug>')
api.add_resource(ProjectList, '/api/projects')
api.add_resource(ProjectDetail, '/api/projects/<string:slug>')


class ProjectsView(FlaskView):
    route_base = '/'

    def get(self):
        res = builds_schema.dump(Build.select().limit(25))
        projects = projects_schema.dump(Project.select())
        return render_template('build_list.html',
                               object_list=res.data,
                               projects_list=projects.data)

    def post(self):
        app.logger.info('Got POST pipeline_receiver', {'host': request.host,
                                                       'url': request.url,
                                                       'remote_addr': request.remote_addr})

        resp = perform(pipeline_yaml=request.data.decode('utf-8'))

        return jsonify({'message': 'Thanks', 'resp': resp})


ProjectsView.register(app)
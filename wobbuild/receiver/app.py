from flask import Flask, request, jsonify, render_template
from flask.ext.classy import FlaskView

from wobbuild.app_logger import gelf_handler
from wobbuild.receiver.models import Project, Build
from wobbuild.fabfile import perform

app = Flask(__name__)
app.logger.addHandler(gelf_handler)


class ProjectsView(FlaskView):
    route_base = '/'

    def get(self):
        return render_template('project_list.html',
                               project_list=Project.select())


    def post(self):
        app.logger.info('Got POST pipeline_receiver', {'host': request.host, 'url': request.url, 'remote_addr': request.remote_addr})

        resp = perform(request.data)

        return jsonify({'message': 'Thanks', 'resp': resp})

ProjectsView.register(app)
from flask import Flask, request, jsonify, render_template
from flask_classy import FlaskView

from wobbuild.app_logger import gelf_handler
from wobbuild.receiver.models import Project, Build
from wobbuild.fabfile import perform

app = Flask(__name__)
app.logger.addHandler(gelf_handler)
app.config['TEMPLATES_AUTO_RELOAD'] = True


class ProjectsView(FlaskView):
    route_base = '/'

    def get(self):
        return render_template('project_list.html',
                               project_list=Project.select())

    def post(self):
        app.logger.info('Got POST pipeline_receiver', {'host': request.host, 'url': request.url, 'remote_addr': request.remote_addr})

        is_async = request.args.get('is_async', 'yes') in ['1', 'true', 'yes', 'y']

        resp = perform(pipeline_yaml=request.data,
                       is_async=is_async)

        return jsonify({'message': 'Thanks', 'resp': resp})

ProjectsView.register(app)
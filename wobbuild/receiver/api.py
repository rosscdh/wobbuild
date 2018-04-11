from flask import jsonify
from flask_restful import Resource, reqparse

from wobbuild.receiver.models import Build, Project
from wobbuild.receiver.serializers import build_schema, builds_schema
from wobbuild.receiver.elastic import es

project_parser = reqparse.RequestParser()

build_parser = reqparse.RequestParser()
build_parser.add_argument('log')
build_parser.add_argument('slug')
build_parser.add_argument('pipeline')
build_parser.add_argument('receiver')


class ProjectList(Resource):
    """
    List of Projects
    """
    def get_queryset(self):
        return Project.select()

    def get(self):
        objects_list = self.get_queryset()
        res = builds_schema.dump(objects_list)
        return jsonify(res.data)


class ProjectDetail(Resource):
    """
    Project
    """
    def get_object(self, slug):
        return Project.get(slug=slug)

    def get(self, slug):
        obj = self.get_object(slug=slug)
        res = build_schema.dump(obj)
        return jsonify(res.data)

    def post(self, slug):
        args = project_parser.parse_args()
        obj = self.get_object(slug=slug)
        obj.step_logs = args.get('log')
        obj.status = args.get('status')
        obj.save()

        res = build_schema.dump(obj)
        es_resp = es.index(index=es._projects_index,
                           doc_type='project',
                           body=res.data)

        return jsonify(res.data)


class BuildList(Resource):
    """
    List of Builds
    """
    def get_queryset(self):
        return Build.select()

    def get(self):
        builds = self.get_queryset()
        res = builds_schema.dump(builds)
        return jsonify(res.data)


class BuildDetail(Resource):
    def get_object(self, slug):
        return Build.get(slug=slug)

    def get(self, slug):
        build = self.get_object(slug=slug)
        res = build_schema.dump(build)
        return jsonify(res.data)

    def post(self, slug):
        args = build_parser.parse_args()
        build = self.get_object(slug=slug)
        build.step_logs = args.get('log')
        build.status = 'success'
        build.save()

        res = build_schema.dump(build)
        es_resp = es.index(index=es._builds_index,
                           doc_type='build',
                           body=res.data)
        return jsonify(res.data)


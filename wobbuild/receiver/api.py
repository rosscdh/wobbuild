from flask import jsonify
from flask_restful import Resource, reqparse

from wobbuild.receiver.models import Build
from wobbuild.receiver.serializers import build_schema, builds_schema
from wobbuild.receiver.elastic import es

parser = reqparse.RequestParser()
parser.add_argument('log')
parser.add_argument('slug')
parser.add_argument('pipeline')
parser.add_argument('receiver')


class BuildList(Resource):
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
        args = parser.parse_args()
        build = self.get_object(slug=slug)
        build.step_logs = args.get('log')
        build.status = 'success'
        build.save()

        #build_json = build_schema.jsonify(build)
        res = build_schema.dump(build)
        es_resp = es.index(index=es._builds_index,
                           doc_type="build",
                           body=res.data)
        #import pdb;pdb.set_trace()
        return jsonify(res.data)
        res = build_schema.dump(build)

        #import pdb;pdb.set_trace()
        return jsonify(res.data)
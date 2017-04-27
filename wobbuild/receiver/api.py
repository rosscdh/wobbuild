from flask import jsonify
from flask_restful import Resource

from wobbuild.receiver.models import Build
from wobbuild.receiver.serializers import build_schema, builds_schema


class BuildList(Resource):
    def get_queryset(self):
        return Build.select()

    def get(self):
        build = self.get_queryset()
        res = builds_schema.dump(build)
        return jsonify(res.data)


class BuildDetail(Resource):
    def get_object(self, slug):
        return Build.get(slug=slug)

    def get(self, slug):
        build = self.get_object(slug=slug)
        res = build_schema.dump(build)
        return jsonify(res.data)
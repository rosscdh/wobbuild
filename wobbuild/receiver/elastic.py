from elasticsearch import Elasticsearch#, helpers as es_helpers

mapping = {
    "mappings": {
        "slug": {"type": "string"},
        "project": {"type": "string"},
        "dateof": {"type": "date"},
        "repo": {"type": "string"},
        "status": {"type": "string"},
        "pipeline": {"type": "text"},
        "step_logs": {"type": "object"},
    }
}

es = Elasticsearch(["http://127.0.0.1:9200"])
es._builds_index = 'builds'
es.indices.create(index=es._builds_index,
                  ignore=400,
                  body=mapping)

# es.index(index=es._builds_index,
#          doc_type="build",
#          body=build_schema.jsonify(build))

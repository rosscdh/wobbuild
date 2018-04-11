from elasticsearch import Elasticsearch#, helpers as es_helpers


builds_mapping = {
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

projects_mapping = {}


es = Elasticsearch(["http://127.0.0.1:9200"])

es._builds_index = 'builds'
es._projects_index = 'projects'

es.indices.create(index=es._builds_index,
                  ignore=400,
                  body=builds_mapping)
es.indices.create(index=es._projects_index,
                  ignore=400,
                  body=projects_mapping)

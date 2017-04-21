from flask import Flask, request, jsonify

from ..app_logger import gelf_handler
from ..fabfile import perform

app = Flask(__name__)

app.logger.addHandler(gelf_handler)


@app.route('/', methods=['POST'])
def pipeline_receiver():
    app.logger.info('Got POST pipeline_receiver', {'host': request.host, 'url': request.url, 'remote_addr': request.remote_addr})

    resp = perform(request.data)

    return jsonify({'message': 'Thanks', 'resp': resp})
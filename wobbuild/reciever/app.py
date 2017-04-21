from flask import Flask, request, jsonify

from ..fabfile import perform

app = Flask(__name__)


@app.route('/', methods=['POST'])
def pipeline_receiver():
    perform(request.data)
    return jsonify({'message': 'OK'})
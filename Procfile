web: FLASK_DEBUG=1 FLASK_APP=wobbuild/receiver/app.py flask run -h 0.0.0.0 -p 5000
worker: celery -A wobbuild.builder.handler worker --loglevel=info
flower: celery flower -A wobbuild.builder.handler --address=0.0.0.0 --port=5555 --broker=redis://localhost:6379/0 --backend=redis://localhost:6379/1
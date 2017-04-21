web: FLASK_APP=wobbuild/receiver/app.py flask run -h 0.0.0.0 -p 5000
worker: celery -A wobbuild.builder.handler worker --loglevel=info
flower: celery flower -A wobbuild.builder.handler --broker=redis://localhost:6379/0 --backend=redis://localhost:6379/1
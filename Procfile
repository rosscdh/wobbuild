web: FLASK_APP=wobbuild/receiver/app.py flask run
worker: celery -A wobbuild.builder.handler worker --loglevel=info
#flower: celery flower -A wobbuild.builder.handler --broker=redis://192.168.99.100:32814/0 --backend=redis://192.168.99.100:32814/1
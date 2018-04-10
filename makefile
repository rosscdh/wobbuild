.PHONY: bootstrap requirements start worker flower web clean

bootstrap:
	ansible-galaxy install -r requirements.yml
	vagrant up

requirements:
	vagrant ssh -c 'cd /vagrant/;source /vagrant/virtualenv/bin/activate;./virtualenv/bin/pip install -r requirements.txt'

start: web flower slanger worker
	PYTHONPATH=$PYTHONPATH:$PWD FLASK_DEBUG=1 FLASK_APP=wobbuild/receiver/app.py flask run -h 0.0.0.0 -p 5000 --with-threads --debugger

worker:
	celery -A wobbuild.builder.handler worker --loglevel=debug

flower:
	celery flower -A wobbuild.builder.handler --address=0.0.0.0 --port=5555 --broker=redis://localhost:6379/0 --backend=redis://localhost:6379/1

web:
	PYTHONPATH=$PYTHONPATH:$PWD FLASK_DEBUG=1 FLASK_APP=wobbuild/receiver/app.py flask run -h 0.0.0.0 -p 5000 --with-threads --debugger

clean:
	find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

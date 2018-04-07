.PHONY: bootstrap requirements start worker slanger flower web clean

bootstrap:
	ansible-galaxy install -r requirements.yml
	vagrant up

requirements:
	vagrant ssh -c 'cd /vagrant/;source /vagrant/virtualenv/bin/activate;./virtualenv/bin/pip install -r requirements.txt'

start: web flower slanger worker
	PYTHONPATH=$PYTHONPATH:$PWD FLASK_DEBUG=1 FLASK_APP=wobbuild/receiver/app.py flask run -h 0.0.0.0 -p 5000 --with-threads --debugger

worker:
	celery -A wobbuild.builder.handler worker --loglevel=debug

slanger:
	rvm use 1.9.3;slanger --app_key 1234567890 --secret wobbuild-secret

flower:
	vagrant ssh -c 'cd /vagrant/;source /vagrant/virtualenv/bin/activate;./virtualenv/bin/honcho start flower'

web:
	PYTHONPATH=$PYTHONPATH:$PWD FLASK_DEBUG=1 FLASK_APP=wobbuild/receiver/app.py flask run -h 0.0.0.0 -p 5000 --with-threads --debugger

clean:
	find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

bootstrap:
	ansible-galaxy install -r requirements.yml
	vagrant up

start:
	vagrant ssh -c 'cd /vagrant/;source ./virtualenv/bin/activate;./virtualenv/bin/honcho start'

post:
	http POST http://192.168.50.5:5000 < wobbuild/wobbuild.example.yml

clean:
	find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

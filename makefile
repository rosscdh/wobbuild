bootstrap:
	ansible-galaxy install -r requirements.yml
	vagrant up

start:
	vagrant ssh -c 'cd /vagrant/;source /vagrant/virtualenv/bin/activate;./virtualenv/bin/honcho start'

worker:
	vagrant ssh -c 'cd /vagrant/;source /vagrant/virtualenv/bin/activate;./virtualenv/bin/honcho start worker'

flower:
	vagrant ssh -c 'cd /vagrant/;source /vagrant/virtualenv/bin/activate;./virtualenv/bin/honcho start flower'

web:
	vagrant ssh -c 'cd /vagrant/;source /vagrant/virtualenv/bin/activate;./virtualenv/bin/honcho start web'

wob:
	#http POST http://192.168.50.5:5000 < $(path)
	fab -f client/fabfile.py build:$(path)

clean:
	find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

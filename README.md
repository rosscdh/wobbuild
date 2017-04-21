# wobbuild
Yet another simple build and deploy system


### Install

1. pip install ansible
2. install vagrant
3. `make bootstrap`

OR

1. `mkvirtualenv wobbuild`
2. `pip install -r requirements.txt`
3. `honcho start`


### Using it


1. `make run`  __starts the services__
2. `make post` __http posts a test yml file__

OR

1. http POST http://localhost:5000 < wobbuild/wobbuild.example.yml
2. this will turn into a command like `coconut build` which will then look for the wobbuild.yml and send it to the receiver endpoint
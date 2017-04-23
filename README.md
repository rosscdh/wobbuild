# wobbuild

Yet another simple build and deploy system.

But this one, can be run by developers so that build time is not centralised.
Publishes artifacts to an artifactory
Integrates with Salt so that deploy orchestration calls can be made



### Install

1. pip install ansible
2. install vagrant
3. `make bootstrap`
4. `make models`


### Using it


1. `make run`  __starts the services__ - This starts the core services
2. browse to `http://192.168.50.5:5000` - This is the public interface
3. `make post path=/path/to/project/with/git/and/a/wobbuild.yml` __http posts a test yml file__ - This is the startings of the client that will be distributed


## Client

A pex file called `wob` that will allow developers to execute commands like

`wob build:/Users/rosscdh/p/my-project/wobbuild.yml`

Which will then build and publish artifacts that the developer can then

`wob deploy:project-name.1.2.3`


## Todo

1. Tests
2. Package Client
3. Pipeline Schema validation
4. Integrate with artifactory
5. Build Deploy process (call salt command with appropriate values)
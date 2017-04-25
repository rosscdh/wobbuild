# wobbuild

Yet another simple build and deploy system.

A bit like travis, but simpler and Open Source.

But this one, can be run by developers so that build time is not centralised.
Publishes artifacts to an artifactory
Integrates with Salt so that deploy orchestration calls can be made



### Install

1. pip install ansible
2. install vagrant
3. `make bootstrap`

`npm install -g grommet-cli`


### Using it


1. `make run`  __starts the services__ - This starts the core services
2. browse to `http://192.168.50.5:5000` - This is the public interface
3. `make wob path=/path/to/project/with/git/and/a/wobbuild.yml` __http posts a test yml file__ - This is the startings of the client that will be distributed


### In Projects

Copy this example into one of your projects

```
language: java
clean: false

repo:
  name: my-patternlab-project
  url: ssh://git@git.dglecom.net:7999/path/to/some/repo.git
  branch: doc/packaging-deploy


#
# Vars gets merged with the GLOBAL_VARS params
#
vars:
  A_VARIABLE: 'foo'
  A_VARIABLE_AGAIN: 'bar'


build_group_matcher:
  master: master
  feature: feature/ITDEV-(\d+)
  release: release/(.+)


#
# Master Branch
# Usually For deploy
#
master:
  before_steps:
    - echo "Message to slack"
    # - n v7.5.0
    # - cd patternlab;npm install

  build:
    do: true
    steps:
      - cd patternlab;npm test
      - cd patternlab;npm publish

  publish:
    do: true
    steps:
      - echo "Upload to artifactory"

  deploy:
    do: true
    steps:
      - echo "Deploy using whatever"
      - echo "Step required"

  final_steps:
    - echo "Message to slack"
    - echo "send email"

#
# Feature branches
# Usually just get tested built and packaged
#
feature:
  before_steps:
    - echo "Message to slack"
    # - n v7.5.0
    # - cd patternlab;npm install

  build:
    do: true
    steps:
      - cd patternlab;npm test
      - cd patternlab;npm publish

  publish:
    do: true
    steps:
      - echo "Upload to artifactory"

  deploy:
    do: false
    steps:
      - echo "Upload to artifactory"

  final_steps:
    - echo "Message to slack"


#
# Release branch steps
# Releases usually involve a publish step
#
release:
  before_steps:
    - echo "Message to slack"
    # - n v7.5.0
    # - cd patternlab;npm install

  build:
    do: true
    steps:
      - cd patternlab;npm test
      - cd patternlab;npm publish

  publish:
    do: true
    steps:
      - echo "Upload to artifactory"

  deploy:
    do: false
    steps:
      - echo "Upload to artifactory"

  final_steps:
    - echo "Message to slack"

```

### How it currently looks

yes yes.. im not a designer, actually no i kinda am.. but aint no body got time for dat.

![uggers](preview.png "Ugly Preview")


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
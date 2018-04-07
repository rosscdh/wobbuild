# wobbuild

Yet another simple build and deploy system.

A bit like travis, but simpler and Open Source.

But this one, can be run by developers so that build time is not centralised.
Publishes artifacts to an artifactory
Integrates with Salt so that deploy orchestration calls can be made


### Using it


1. `docker-compose up`
2. browse to `http://localhost:5000` - This is the public interface
3. install the client `cd client;python setup.py install`
4. setup the .wobbuild.yml in the repo you would have built (copy wobbuild/wobbuid.example.yml)
5. wobbuild ../path/to/project/.wobbuild.yml --target http://localhost:5000


### In Projects

Copy this example into one of your projects

```
language: java
clean: false

repo:
  name: my-patternlab-project
  url: ssh://git@git.example.net:7999/path/to/some/repo.git


#
# Vars gets merged with the GLOBAL_VARS params
#
vars:
  A_VARIABLE: 'foo'
  A_VARIABLE_AGAIN: 'bar'


#
# Match up the build_groups with the appropriate git branches
#
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

yes yes.. im not a designer. aint no body got time for dat.

![uggers](preview.png "Ugly Preview")


## Client

A docker image can be run to work like this

`wob build:/Users/rosscdh/p/my-project/wobbuild.yml`

Which will then build and publish artifacts that the developer can then

`wob deploy:project-name.1.2.3`


## Todo

1. Tests
2. Package Client
3. Pipeline Schema validation
4. Integrate with artifactory
5. Build Deploy process (call salt command with appropriate values)

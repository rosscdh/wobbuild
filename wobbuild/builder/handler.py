import os
import yaml
import pprint

from celery import Celery

from jinja2 import Template

from fabric.api import lcd, local

celery_app = Celery('tasks',
                    backend='redis://192.168.99.100:32814/1',
                    broker='redis://192.168.99.100:32814/0')


@celery_app.task
def perform_pipeline(context, pipeline_template):
    pipeline = yaml.load(pipeline_template)
    BASE_PATH = pipeline.get('BASE_PATH')
    pprint.pprint(pipeline)

    builds_path = os.path.join(BASE_PATH, 'builds')
    the_build_path = os.path.join(builds_path, pipeline.get('repo').get('name'))

    repo = pipeline.get('repo', {})

    if pipeline.get('clean') is True:
        local('rm -Rf {the_build_path}'.format(the_build_path=the_build_path))

    if not os.path.exists(the_build_path):
        with lcd(builds_path):

            if not os.path.exists(the_build_path):
                local('git clone {url}'.format(url=repo.get('url')))

    with lcd(the_build_path):
        local('git checkout {branch}'.format(branch=repo.get('branch')))

    for step in pipeline.get('steps'):
        perform_step(path=the_build_path, step=step)


@celery_app.task
def perform_step(the_build_path, step):
    #print 'cd {the_build_path}'.format(the_build_path=the_build_path)
    with lcd(the_build_path):
        return local(step)

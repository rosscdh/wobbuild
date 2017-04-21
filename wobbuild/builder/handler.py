import os
import yaml
import pprint

from celery import Celery

from fabric.api import lcd, local
from wobbuild.settings import GLOBAL_VARS
from wobbuild.app_logger import logger


celery_app = Celery('tasks',
                    backend=GLOBAL_VARS.get('redis').get('backend'),
                    broker=GLOBAL_VARS.get('redis').get('broker'))


@celery_app.task
def perform_pipeline(context, pipeline_template):
    pipeline = yaml.load(pipeline_template)

    logger.debug('pipeline yaml', {'pipeline': pipeline})

    builds_path = context.get('builds_path')

    logger.debug('create builds path', {'builds_path': builds_path})
    local('mkdir -p {builds_path}'.format(builds_path=builds_path))

    the_build_path = os.path.join(builds_path, pipeline.get('repo').get('name'))

    repo = pipeline.get('repo', {})

    if pipeline.get('clean') is True:
        logger.info('clean build path', {'builds_path': builds_path})
        local('rm -Rf {the_build_path}'.format(the_build_path=the_build_path))

    if not os.path.exists(the_build_path):
        with lcd(builds_path):
            if not os.path.exists(the_build_path):
                logger.info('clone repository', {'the_build_path': the_build_path, 'repo': repo})
                local('git clone {url}'.format(url=repo.get('url')))

    with lcd(the_build_path):
        logger.info('checkout branch', {'the_build_path': the_build_path})
        local('git checkout {branch}'.format(branch=repo.get('branch')))

    for step in pipeline.get('before_steps', []):
        logger.info('perform before_step', {'step': step})
        perform_step(path=the_build_path, step=step)

    build = pipeline.get('build', {})
    if build.get('do') is True:
        for step in build.get('steps', []):
            logger.info('perform build.step', {'step': step})
            perform_step(path=the_build_path, step=step)

    deploy = pipeline.get('deploy', {})
    if deploy.get('do') is True:
        for step in deploy.get('steps', []):
            logger.info('perform deploy.step', {'step': step})
            perform_step(path=the_build_path, step=step)

    for step in pipeline.get('final_steps', []):
        logger.info('perform final_steps', {'step': step})
        perform_step(path=the_build_path, step=step)


def perform_step(path, step):
    #print 'cd {the_build_path}'.format(the_build_path=the_build_path)
    with lcd(path):
        return local(step)

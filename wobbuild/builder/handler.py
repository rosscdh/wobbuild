import os
import timy
import yaml
from timy.settings import (
    timy_config,
    TrackingMode
)

#import pprint

from celery import Celery
from celery.signals import (before_task_publish,
                            after_task_publish,
                            task_prerun,
                            task_postrun,
                            task_retry,
                            task_success,
                            task_failure,
                            task_revoked,
                            task_unknown,
                            task_rejected,)

from fabric.api import settings, lcd, local

from wobbuild.settings import GLOBAL_VARS
from wobbuild.app_logger import logger

from wobbuild.receiver.models import Project, Build

timy_config.tracking_mode = TrackingMode.LOGGING

celery_app = Celery('tasks',
                    backend=GLOBAL_VARS.get('redis').get('backend'),
                    broker=GLOBAL_VARS.get('redis').get('broker'))


@celery_app.task(bind=True)
def perform_pipeline(self, context, pipeline_template):
    pipeline = yaml.load(pipeline_template)  # used to be sent as yaml

    BUILD_LOG = {
        'system': [],
        'before_steps': [],
        'build_steps': [],
        'publish_steps': [],
        'deploy_steps': [],
        'final_steps': [],
    }

    logger.info('Celery Task: %s' % self.request.id)
    logger.debug('pipeline yaml', {'pipeline': pipeline})

    repo = pipeline.get('repo', {})
    project, is_new = Project.get_or_create(name=repo.get('name'))
    project.data = repo
    project.save()

    build, is_new = Build.get_or_create(project=project, slug=str(self.request.id))
    build.pipeline = pipeline
    build.save()

    builds_path = context.get('builds_path')

    logger.debug('create builds path: {builds_path}', {'builds_path': builds_path})
    cmd = 'mkdir -p {builds_path}'.format(builds_path=builds_path)
    res = local(cmd, capture=True)
    log_step('create_build_path', BUILD_LOG, res, cmd)

    the_build_path = os.path.join(builds_path, pipeline.get('repo').get('name'), 'repo')

    repo = pipeline.get('repo', {})

    if pipeline.get('clean') is True:
        logger.info('clean build path', {'builds_path': builds_path})
        cmd = 'rm -Rf {the_build_path}'.format(the_build_path=the_build_path)
        res = local(cmd, capture=True)
        log_step('clean_build_path', BUILD_LOG, res, cmd)

    if not os.path.exists(the_build_path):
        with lcd(builds_path):
            if not os.path.exists(the_build_path):
                logger.info('clone repository', {'the_build_path': the_build_path, 'repo': repo})
                cmd = 'git clone {url} {the_build_path}'.format(url=repo.get('url'), the_build_path=the_build_path)
                res = local(cmd, capture=True)
                log_step('clone_repo', BUILD_LOG, res, cmd)

    with lcd(the_build_path):
        logger.info('checkout branch', {'the_build_path': the_build_path})
        cmd = 'git checkout {branch}'.format(branch=repo.get('branch'))
        res = local(cmd, capture=True)
        log_step('git_checkout_branch', BUILD_LOG, res, cmd)

    build_pipeline = pipeline.get('build')

    with timy.Timer() as timer:
        for r, step in before_steps(build_pipeline, the_build_path):
            log_step('before_steps', BUILD_LOG, r, step)

    with timy.Timer() as timer:
        for r, step in build_steps(build_pipeline, the_build_path):
            log_step('build_steps', BUILD_LOG, r, step)

    with timy.Timer() as timer:
        for r, step in publish_steps(build_pipeline, the_build_path):
            log_step('publish_steps', BUILD_LOG, r, step)

    with timy.Timer() as timer:
        for r, step in deploy_steps(build_pipeline, the_build_path):
            log_step('deploy_steps', BUILD_LOG, r, step)

    with timy.Timer() as timer:
        for r, step in final_steps(build_pipeline, the_build_path):
            log_step('final_steps', BUILD_LOG, r, step)

    build.step_logs = BUILD_LOG
    build.save()


def before_steps(pipeline, the_build_path):
    for step in pipeline.get('before_steps', []):
        logger.info('perform before_step', {'step': step})
        yield perform_step(path=the_build_path, step=step), step


def build_steps(pipeline, the_build_path):
    build = pipeline.get('build', {})
    if build.get('do') is True:
        for step in build.get('steps', []):
            logger.info('perform build.step', {'step': step})
            yield perform_step(path=the_build_path, step=step), step


def publish_steps(pipeline, the_build_path):
    publish = pipeline.get('publish', {})
    if publish.get('do') is True:
        for step in publish.get('steps', []):
            logger.info('perform publish.step', {'step': step})
            yield perform_step(path=the_build_path, step=step), step


def deploy_steps(pipeline, the_build_path):
    deploy = pipeline.get('deploy', {})
    if deploy.get('do') is True:
        for step in deploy.get('steps', []):
            logger.info('perform deploy.step', {'step': step})
            yield perform_step(path=the_build_path, step=step), step


def final_steps(pipeline, the_build_path):
    for step in pipeline.get('final_steps', []):
        logger.info('perform final_steps', {'step': step})
        yield perform_step(path=the_build_path, step=step), step


def perform_step(path, step):
    with settings(warn_only=True):
        with lcd(path):
            res = local(step, capture=True)
            return res


def log_step(step_type, BUILD_LOG, result, step):
    step_type = 'system' if step_type not in BUILD_LOG.keys() else step_type
    event = {
        'step_type': step_type,
        'step': step,
        'result': result.stdout or result.stderr,
    }
    BUILD_LOG[step_type].append(event)


@task_failure.connect
def task_failure_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    print kwargs

@task_rejected.connect
def task_rejected_handler(sender=None, headers=None, body=None, **kwargs):
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    print kwargs

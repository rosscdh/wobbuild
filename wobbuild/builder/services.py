import os
import timy

from collections import OrderedDict

from timy.settings import (
    timy_config,
    TrackingMode
)

from fabric.api import settings, lcd, local

from wobbuild.app_logger import logger

from wobbuild.receiver.models import Project, Build
from wobbuild.builder.exceptions import BuildFailedException

timy_config.tracking_mode = TrackingMode.LOGGING


class Failedresult(object):
    return_code = 500

    def __repr__(self):
        return 'skipped'


class BuilderService(object):
    logger = logger

    def __init__(self, build_id, context, pipeline, *args, **kwargs):
        self.BUILD_LOG = {
            'system': [],
            'before_steps': [],
            'build_steps': [],
            'publish_steps': [],
            'deploy_steps': [],
            'final_steps': [],
        }
        self.has_failed = None

        self.build_id = build_id
        self.context = context
        self.pipeline = pipeline

        self.repo = self.pipeline.get('repo', {})

        self.project, is_new = Project.get_or_create(name=self.repo.get('name'))
        self.project.data = self.repo
        self.project.save()

        self.build, is_new = Build.get_or_create(project=self.project, slug=str(self.build_id), status='created')
        self.build.pipeline = self.pipeline
        self.build.save()

        self.builds_path = context.get('builds_path')
        self.the_build_path = os.path.join(self.builds_path, self.pipeline.get('repo').get('name'), 'repo')

    def process(self):
        self.init_project()
        self.build_the_pipeline()

    def init_project(self):
        self.logger.debug('create builds path: {builds_path}', {'builds_path': self.builds_path})

        cmd = 'mkdir -p {builds_path}'.format(builds_path=self.builds_path)
        with timy.Timer() as timer:
            res = local(cmd, capture=True)
            self.log_step(step_type='create_build_path',
                          result=res,
                          return_code=res.return_code,
                          is_successful=res.return_code == 0,
                          step=cmd,
                          took=timer.elapsed)

        if self.pipeline.get('clean') is True:
            with timy.Timer() as timer:
                self.logger.info('clean build path', {'builds_path': self.builds_path})
                cmd = 'rm -Rf {the_build_path}'.format(the_build_path=self.the_build_path)
                res = local(cmd, capture=True)
                self.log_step(step_type='clean_build_path',
                              result=res,
                              return_code=res.return_code,
                              is_successful=res.return_code == 0,
                              step=cmd,
                              took=timer.elapsed)

        if not os.path.exists(self.the_build_path):
            with lcd(self.builds_path):
                if not os.path.exists(self.the_build_path):
                    with timy.Timer() as timer:
                        self.logger.info('clone repository', {'the_build_path': self.the_build_path, 'repo': self.repo})
                        cmd = 'git clone {url} {the_build_path}'.format(url=self.repo.get('url'), the_build_path=self.the_build_path)
                        res = local(cmd, capture=True)
                        self.log_step(step_type='clone_repo',
                                      result=res,
                                      return_code=res.return_code,
                                      is_successful=res.return_code == 0,
                                      step=cmd,
                                      took=timer.elapsed)

        with lcd(self.the_build_path):
            with timy.Timer() as timer:
                self.logger.info('checkout branch', {'the_build_path': self.the_build_path})
                cmd = 'git checkout {branch}'.format(branch=self.repo.get('branch'))
                res = local(cmd, capture=True)
                self.log_step(step_type='git_checkout_branch',
                              result=res,
                              return_code=res.return_code,
                              is_successful=res.return_code == 0,
                              step=cmd,
                              took=timer.elapsed)

    def build_the_pipeline(self):
        build_pipeline = self.pipeline.get('build')

        pipeline_steps = OrderedDict([
            ('before_steps', self.before_steps),
            ('build_steps', self.build_steps),
            ('publish_steps', self.publish_steps),
            ('deploy_steps', self.deploy_steps),
            ('final_steps', self.final_steps),
        ])

        for builder_step in pipeline_steps.keys():

            with timy.Timer() as timer:

                for result, step in pipeline_steps.get(builder_step)(pipeline=build_pipeline):

                    is_successful = result.return_code == 0
                    self.logger.debug(step)
                    self.log_step(step_type=builder_step,
                                  result=result,
                                  return_code=result.return_code,
                                  is_successful=is_successful,
                                  step=step,
                                  took=timer.elapsed)

                    if is_successful is False:
                        msg = 'Build {id} Failed: {step} with return_code: {return_code} result: {result}'.format(id=self.build_id,
                                                                                                                  step=step,
                                                                                                                  result=result,
                                                                                                                  return_code=result.return_code)
                        self.logger.error(msg)
                        raise BuildFailedException(msg)

    def before_steps(self, pipeline):
        for step in pipeline.get('before_steps', []):
            logger.info('perform before_step', {'step': step})
            yield self.perform_step(path=self.the_build_path, step=step), step

    def build_steps(self, pipeline):
        build = pipeline.get('build', {})
        if build.get('do') is True:
            for step in build.get('steps', []):
                logger.info('perform build.step', {'step': step})
                yield self.perform_step(path=self.the_build_path, step=step), step

    def publish_steps(self, pipeline):
        publish = pipeline.get('publish', {})
        if publish.get('do') is True:
            for step in publish.get('steps', []):
                logger.info('perform publish.step', {'step': step})
                yield self.perform_step(path=self.the_build_path, step=step), step

    def deploy_steps(self, pipeline):
        deploy = pipeline.get('deploy', {})
        if deploy.get('do') is True:
            for step in deploy.get('steps', []):
                logger.info('perform deploy.step', {'step': step})
                yield self.perform_step(path=self.the_build_path, step=step), step

    def final_steps(self, pipeline):
        for step in pipeline.get('final_steps', []):
            logger.info('perform final_steps', {'step': step})
            yield self.perform_step(path=self.the_build_path, step=step), step

    def perform_step(self, path, step):
        if self.has_failed is True:
            return Failedresult()

        with settings(warn_only=True):
            with lcd(path):
                res = local(step, capture=True)
                return res

    def log_step(self, step_type, result, return_code, is_successful, step, took):
        if self.has_failed is None:
            self.has_failed = True if is_successful is False else None

        step_type = 'system' if step_type not in self.BUILD_LOG.keys() else step_type
        event = {
            'step_type': step_type,
            'step': step,
            'result': result.stdout or result.stderr,
            'is_successful': is_successful,
            'return_code': return_code,
            'took': took,
        }
        self.BUILD_LOG[step_type].append(event)
        self.build.step_logs = self.BUILD_LOG

        if is_successful is False:
            self.build.status = 'failure' 

        self.build.save()

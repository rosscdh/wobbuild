import os
import timy

from jinja2 import Template

from collections import OrderedDict

from timy.settings import (
    timy_config,
    TrackingMode
)

from fabric.api import settings, lcd, local, shell_env

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
        """
        @TODO turn these steps into a seperate service
        """
        self.logger.debug('create builds path: {builds_path}', {'builds_path': self.builds_path})

        # Create the builds path
        cmd = 'mkdir -p {builds_path}'.format(builds_path=self.builds_path)
        with timy.Timer() as timer:
            res = local(cmd, capture=True)
            self.log_step(step_type='create_build_path',
                          result=res,
                          return_code=res.return_code,
                          is_successful=res.return_code == 0,
                          step=cmd,
                          took=timer.elapsed)

        #
        # Perform a clean if specified
        #
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

        #
        # if the build_path doesnt exist then create
        #
        if not os.path.exists(self.the_build_path):
            # step into the place we store our builds
            with lcd(self.builds_path):
                # clone the repo
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

        #
        # Checkout the requested branch
        #
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
            self.logger.info('perform before_step', {'step': step})
            yield self.perform_step(step=step), step

    def build_steps(self, pipeline):
        build = pipeline.get('build', {})
        if build.get('do') is True:
            for step in build.get('steps', []):
                self.logger.info('perform build.step', {'step': step})
                yield self.perform_step(step=step), step

    def publish_steps(self, pipeline):
        publish = pipeline.get('publish', {})
        if publish.get('do') is True:
            for step in publish.get('steps', []):
                self.logger.info('perform publish.step', {'step': step})
                yield self.perform_step(step=step), step

    def deploy_steps(self, pipeline):
        deploy = pipeline.get('deploy', {})
        if deploy.get('do') is True:
            for step in deploy.get('steps', []):
                self.logger.info('perform deploy.step', {'step': step})
                yield self.perform_step(step=step), step

    def final_steps(self, pipeline):
        for step in pipeline.get('final_steps', []):
            self.logger.info('perform final_steps', {'step': step})
            yield self.perform_step(step=step), step

    def perform_step(self, step):
        if self.has_failed is True:
            return Failedresult()

        with settings(warn_only=True):

            # Set the environment Variables
            env_variables = self.pipeline.get('vars')
            if not env_variables:
                env_variables = {}
            #env_variables.update(self.context)
            env_variables.update({
                'has_failed': str(self.has_failed) if self.has_failed else '0',
            })
            self.logger.debug('set env_variables {env_variables}'.format(env_variables=env_variables), env_variables)

            # Turn the step into a jinja template
            step = Template(step)
            step = step.render(**env_variables)

            # set the env vars in the shell
            with shell_env(**env_variables):
                # cd into the build path
                with lcd(self.the_build_path):
                    # execute the now templaterized step
                    return local(step, capture=True)

    def log_step(self, step_type, result, return_code, is_successful, step, took):
        if self.has_failed is None:
            self.has_failed = True if is_successful is False else None

        # if we have a new build type that has no handler set it to system
        step_type = 'system' if step_type not in self.BUILD_LOG.keys() else step_type

        event = {
            'step_type': step_type,
            'step': step,
            'result': result.stdout or result.stderr,
            'is_successful': is_successful,
            'return_code': return_code,
            'took': took,
        }
        # append to build
        self.BUILD_LOG[step_type].append(event)
        # update the builds logs
        self.build.step_logs = self.BUILD_LOG

        # oh we failed.. set the status
        if is_successful is False:
            self.build.status = 'failure' 

        #self.build.save()
        query = Build.update(step_logs=self.BUILD_LOG, status=self.build.status).where(id == self.build.id)
        query.execute()

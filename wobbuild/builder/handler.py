import ruamel.yaml as yaml

from timy.settings import (
    timy_config,
    TrackingMode
)

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

from wobbuild.settings import GLOBAL_VARS

from wobbuild.receiver.models import Build
from wobbuild.builder.services import BuilderService

timy_config.tracking_mode = TrackingMode.LOGGING

celery_app = Celery('tasks',
                    backend=GLOBAL_VARS.get('redis').get('backend'),
                    broker=GLOBAL_VARS.get('redis').get('broker'))


@celery_app.task(bind=True)
def perform_pipeline(self, context, pipeline_template):
    pipeline = yaml.load(pipeline_template, Loader=yaml.RoundTripLoader)  # used to be sent as yaml
    service = BuilderService(build_id=self.request.id,
                             context=context,
                             pipeline=pipeline)
    service.process()


@task_success.connect
def task_success_handler(sender=None, headers=None, body=None, **kwargs):
    pass
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    # print 'SUCCESS:'
    # print sender.request.id
    # build = Build.get(Build.slug == sender.request.id)
    # print build
    # build.status = 'success'
    # build.save()
    # print kwargs


@task_failure.connect
def task_failure_handler(sender=None, headers=None, body=None, **kwargs):
    pass
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    # print sender
    # build = Build.get(Build.slug == sender.request.id)
    # print build
    # build.status = 'failure'
    # build.save()
    # print kwargs


@task_rejected.connect
def task_rejected_handler(sender=None, headers=None, body=None, **kwargs):
    pass
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    # print sender
    # build = Build.get(Build.slug == sender.request.id)
    # print build
    # build.status = 'rejected'
    # build.save()
    # print kwargs

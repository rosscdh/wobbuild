import requests
from urllib.parse import urljoin

import ruamel.yaml as yaml

from timy.settings import (
    timy_config,
    TrackingMode
)

from pusher import Pusher

from celery import Celery
from celery.contrib import rdb
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
from wobbuild.app_logger import logger
from wobbuild.receiver.models import Build
from wobbuild.builder.services import BuilderService

timy_config.tracking_mode = TrackingMode.LOGGING

# PUSHER = Pusher(app_id=u'1',
#                 key=u'1234567890',
#                 secret=u'wobbuild-secret',
#                 host=u'192.168.50.5',
#                 port=4567,
#                 ssl=False)

PUSHER = Pusher(**GLOBAL_VARS.get('push', {}))


celery_app = Celery('tasks',
                    backend=GLOBAL_VARS.get('redis').get('backend'),
                    broker=GLOBAL_VARS.get('redis').get('broker'))


class PusherEvent(object):
    def __init__(self, *args, **kwargs):
        self.client = PUSHER

    def send(self, channel, event, *args, **kwargs):
        self.client.trigger(channel, event, kwargs)

pusher = PusherEvent()


@celery_app.task(bind=True)
def perform_pipeline(self, context, pipeline):
    service = BuilderService(build_id=self.request.id,
                             context=context,
                             pipeline=pipeline)
    return service.process()


@task_success.connect
def task_success_handler(sender=None, headers=None, body=None, result={}, **kwargs):
    logger.info('Success!!!')
    #rdb.set_trace()
    # print(kwargs)
    # print(body)
    slug = result.get('slug')
    url = urljoin(result.get('receiver'), '/api/builds/{slug}'.format(slug=slug))
    resp = requests.post(url, json=result)
    print('Posted: {}'.format(resp.ok))
    pusher.send(channel='build-{}'.format(slug), event='build-complete', data={'build_id': slug, 'result': result})
    pusher.send(channel=u'builds', event=u'build-complete', data={'build_id': slug, 'result': result})


@task_failure.connect
def task_failure_handler(sender=None, headers=None, body=None, result=None, **kwargs):
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
def task_rejected_handler(sender=None, headers=None, body=None, result=None, **kwargs):
    pass
    # information about task are located in headers for task messages
    # using the task protocol version 2.
    # print sender
    # build = Build.get(Build.slug == sender.request.id)
    # print build
    # build.status = 'rejected'
    # build.save()
    # print kwargs

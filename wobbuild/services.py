import os
import ruamel.yaml as yaml

import uuid
import pprint

from .app_logger import logger

from jinja2 import Template

from .builder.handler import perform_pipeline
from .builder.services import BuilderService
from .settings import GLOBAL_VARS


def perform(pipeline_yaml, is_async=False):
    pipeline_template = Template(pipeline_yaml)
    pipeline_template = pipeline_template.render(**GLOBAL_VARS)

    logger.debug('performing pipeline', {'pipeline_yaml': pipeline_yaml, 'GLOBAL_VARS': GLOBAL_VARS, 'is_async': is_async})

    is_async = False
    if is_async is True:
        # do it async
        perform_pipeline.delay(GLOBAL_VARS, pipeline_template)
    else:
        # do it sync for debugging
        pipeline = yaml.load(pipeline_template, Loader=yaml.RoundTripLoader)  # used to be sent as yaml
        service = BuilderService(build_id=str(uuid.uuid1())[:8],
                                 context=GLOBAL_VARS,
                                 pipeline=pipeline)
        service.process()

    return {'pipeline': pprint.pformat(pipeline_template)}


def receive_pipeline(pipeline_yaml):
    perform(pipeline_yaml=pipeline_yaml)


def read_pipeline(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)


def build(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)


def publish(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)


def deploy(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)

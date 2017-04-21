import os
import pprint

from app_logger import logger

from jinja2 import Template

from fabric.api import task

from builder.handler import perform_pipeline
from wobbuild.settings import GLOBAL_VARS


def perform(pipeline_yaml):
    pipeline_template = Template(pipeline_yaml)
    pipeline_template = pipeline_template.render(**GLOBAL_VARS)

    logger.debug('performing pipeline', {'pipeline_yaml': pipeline_yaml, 'GLOBAL_VARS': GLOBAL_VARS})

    perform_pipeline.delay(GLOBAL_VARS, pipeline_template)

    return {'pipeline': pprint.pformat(pipeline_template)}


@task
def receive_pipeline(pipeline_yaml):
    perform(pipeline_yaml=pipeline_yaml)


@task
def read_pipeline(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)

import os
import click

#from celery import current_app
from wobbuild.builder.handler import celery_app
from celery.bin import worker as celery_worker


TRUTHY = [1, '1', 't', 'y', 'true', 'True', True]

#
# Worker
#


@click.group()
def worker():
    pass


@worker.command()
@click.option('--broker',
              default='http://localhost:6379',
              help='Redis broker. http://localhost:6379')
@click.option('--loglevel',
              default='debug',
              help='Loglevel. debug|info|warn|error|critical')
def start(broker, loglevel):
    """ Start server """
    #app = current_app._get_current_object()

    celery_worker_instance = celery_worker.worker(app=celery_app)

    options = {
        'broker': os.getenv('CELERY_BROKER', broker),
        'loglevel': os.getenv('CELERY_LOGLEVEL', loglevel),
        'traceback': True,
    }

    celery_worker_instance.run(**options)


cli = click.CommandCollection(sources=[worker])


if __name__ == '__main__':
    cli()()
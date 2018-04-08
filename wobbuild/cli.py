import os
import click

TRUTHY = [1, '1', 't', 'y', 'true', 'True', True]

#
# Worker
#

@click.group()
def worker():
    pass

@worker.command()
def work():
    """ Start server """

#
# Server
#
@click.group()
def server():
    pass

@server.command()
def serve():
    """ Start server """
    setattr(os.environ, 'PYTHONPATH', '{}:{}'.format(os.getenv('PYTHONPATH'), os.getenv('PWD')))
    setattr(os.environ, 'FLASK_DEBUG', '{}'.format(os.getenv('FLASK_DEBUG', 1)))
    setattr(os.environ, 'FLASK_APP', 'wobbuild/receiver/app.py')
    from wobbuild.receiver.app import app
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', True) in TRUTHY)
    #flask run -h 0.0.0.0 -p 5000 --with-threads --debugger


cli = click.CommandCollection(sources=[worker, server])


if __name__ == '__main__':
    cli()()
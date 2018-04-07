import os
import click
import requests

from wobbuild.services import WobbuildClientService


@click.command()
@click.option('--wob',
              default='./wobbuild.yml',
              help='Path to the .wobbuild.yml')
@click.option('--target',
              default='http://localhost:5000',
              help='The build server url. http://localhost:5000')
def wobbuild(wob, target):
    """Simple program that greets NAME for a total of COUNT times."""
    if not os.path.exists(wob):
        raise click.ClickException('The .wobbuild.yml ({}) does not exist'.format(wob))

    try:
        resp = requests.head(target)
        if not resp.ok:
            raise click.ClickException('The server is not responding ({})'.format(target))

    except requests.exceptions.ConnectionError:
        raise click.ClickException('The server is not responding ({})'.format(target))

    print(wob)
    print(target)
    service = WobbuildClientService(wob=wob)
    service.build()

if __name__ == '__main__':
    wobbuild()
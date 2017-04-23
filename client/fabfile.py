import os
import git

from fabric.api import task



def perform(pipeline_yaml):
    # send to web-reciever
    return {'pipeline': pprint.pformat(pipeline_template)}


@task
def receive_pipeline(pipeline_yaml):
    perform(pipeline_yaml=pipeline_yaml)


@task
def read_pipeline(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)


def git_brach(repo_dir):
        repo = git.Repo(repo_dir)
        branch = repo.active_branch
        return branch.name

@task
def build(pipeline_yaml_path):
    if os.path.isfile(pipeline_yaml_path):
        repo_dir = os.path.dirname(pipeline_yaml_path)
        print git_brach(repo_dir)
        # pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        # perform(pipeline_yaml=pipeline_yaml)


@task
def publish(pipeline_yaml_path):
    if os.path.isfile(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)

@task
def deploy(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)

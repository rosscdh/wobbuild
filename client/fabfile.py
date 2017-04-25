import re
import os
import git
import yaml
import requests

from fabric.api import task

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VARS = yaml.load(open(os.path.join(BASE_PATH, 'vars/default.yml'), 'r').read())
DEFAULT_VARS.update({
    'BASE_PATH': BASE_PATH,
})


def perform(pipeline):
    # send to web-reciever
    url = DEFAULT_VARS.get('wobbuild').get('receiver').get('build')

    pipeline_yaml = yaml.dump(pipeline)
    headers = {
        'Content-Type': 'application/x-yaml'
    }
    resp = requests.post(url, data=pipeline_yaml, headers=headers)

    if resp.ok:
        return resp.json()
    else:
        return resp.content


def git_brach(repo_dir):
        repo = git.Repo(repo_dir)
        branch = repo.active_branch
        return branch.name


def get_pipeline(pipeline_yaml_path):
    return yaml.load(open(pipeline_yaml_path, 'r').read())


def compile_pipeline_to_send(pipeline, branch):
    """
    Extract a matching build_group from the current branch name of the git repo
    then return compile the new branch matcher
    """
    for key, matcher in pipeline.get('build_group_matcher').iteritems():
        m = re.search(matcher, branch)
        if m and len(m.groups()) >= 1:
            matched_build_group = key
            break

    build = pipeline.get(matched_build_group)
    assert build, 'No build_group_matcher was found based on the current branch: {branch}'.format(branch=branch)

    send_pipeline = {
        'language': pipeline.get('language'),
        'clean': pipeline.get('clean'),
        'repo': pipeline.get('repo'),
        'vars': pipeline.get('vars'),
        'build_group_matcher': pipeline.get('build_group_matcher'),
        'build': build
    }
    return send_pipeline


@task
def build(pipeline_yaml_path):
    if os.path.isfile(pipeline_yaml_path):

        pipeline = get_pipeline(pipeline_yaml_path)

        repo_dir = os.path.dirname(pipeline_yaml_path)

        branch = git_brach(repo_dir)

        send_pipeline = compile_pipeline_to_send(pipeline=pipeline,
                                                 branch=branch)

        perform(pipeline=send_pipeline)


@task
def deploy(pipeline_yaml_path):
    if os.path.exists(pipeline_yaml_path):
        pipeline_yaml = open(pipeline_yaml_path, 'r').read()
        perform(pipeline_yaml=pipeline_yaml)

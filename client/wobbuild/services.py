import re
import os
import git
import ruamel.yaml as yaml

import requests

TRUTHY = ('1', 1, 't', 'True', 'true', True)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VARS = yaml.load(open(os.path.join(BASE_PATH, '.wobbuild.defaults.yml'), 'r').read(), Loader=yaml.RoundTripLoader)
DEFAULT_VARS.update({
    'BASE_PATH': BASE_PATH,
})


class DirtyRepoException(Exception): pass


class NoRemoteDefinedException(Exception): pass


class WobbuildClientService:
    wob = None

    def __init__(self, wob, *args, **kwargs):
        if not os.path.isfile(wob):
            raise Exception('{} is not a file'.format(wob))
        self.wob = wob

    def perform(self, pipeline):
        # send to web-reciever
        url = DEFAULT_VARS.get('wobbuild').get('receiver').get('build')

        pipeline_yaml = yaml.dump(pipeline, Dumper=yaml.RoundTripDumper)
        #import pdb;pdb.set_trace()
        headers = {
            'Content-Type': 'application/x-yaml'
        }

        resp = requests.post(url, data=pipeline_yaml, headers=headers)

        if resp.ok:
            return resp.json()
        else:
            return resp.content

    def repo_info(self, repo_dir):
            repo = git.Repo(repo_dir)
            if repo.is_dirty():
                raise DirtyRepoException('The repo is dirty')
            try:
                url = [u for u in repo.remote().urls][0]
            except:
                raise NoRemoteDefinedException('You dont seem to have a remote for this project defined')

            return {
                'name': os.path.basename(url),
                'url': url,
                'branch': str(repo.active_branch),
            }

    def get_pipeline(self):
        return yaml.load(open(self.wob, 'r').read(), Loader=yaml.RoundTripLoader)

    def compile_pipeline_to_send(self, pipeline):
        """
        Extract a matching build_group from the current branch name of the git repo
        then return compile the new branch matcher
        """
        matched_build_group = 'master'
        #print(pipeline.get('build_group_matcher'), branch)

        repo_dir = os.path.dirname(self.wob)
        repo = self.repo_info(repo_dir)

        branch = repo.get('branch')

        for key, matcher in pipeline.get('build_group_matcher').items():
            m = re.search(matcher, branch)
            if m:
                matched_build_group = key
                break

        build = pipeline.get(matched_build_group)
        assert build, 'No build_group_matcher was found based on the current branch: {branch}'.format(branch=branch)

        pipeline_vars = pipeline.get('vars', {})
        pipeline_vars.update({
            'user': os.getenv('USER'),
            'home': os.getenv('HOME'),
        })

        send_pipeline = {
            'async': pipeline.get('async', True) in TRUTHY,
            'language': pipeline.get('language', 'unknown'),
            'clean': pipeline.get('clean', True),
            'repo': repo,
            'vars': pipeline_vars,
            'build_group_matcher': pipeline.get('build_group_matcher'),
            'build': build
        }
        return send_pipeline

    def build(self):
        pipeline = self.get_pipeline()

        send_pipeline = self.compile_pipeline_to_send(pipeline=pipeline)

        self.perform(pipeline=send_pipeline)

    def deploy(self):
        self.perform(pipeline_yaml=self.get_pipeline())

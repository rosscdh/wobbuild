import re
import os
import git
import ruamel.yaml as yaml

import requests

#from fabric.api import task

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VARS = yaml.load(open(os.path.join(BASE_PATH, '.wobbuild.defaults.yml'), 'r').read(), Loader=yaml.RoundTripLoader)
DEFAULT_VARS.update({
    'BASE_PATH': BASE_PATH,
})


class WobbuildClientService:
    wob = None

    def __init__(self, wob, *args, **kwargs):
        self.wob = wob

    def perform(self, pipeline):
        # send to web-reciever
        url = DEFAULT_VARS.get('wobbuild').get('receiver').get('build')

        pipeline_yaml = yaml.dump(pipeline, Dumper=yaml.RoundTripDumper)

        headers = {
            'Content-Type': 'application/x-yaml'
        }
        resp = requests.post(url, data=pipeline_yaml, headers=headers)

        if resp.ok:
            return resp.json()
        else:
            return resp.content

    def git_brach(self, repo_dir):
            repo = git.Repo(repo_dir)
            branch = repo.active_branch
            return branch.name

    def get_pipeline(self):
        return yaml.load(open(self.wob, 'r').read(), Loader=yaml.RoundTripLoader)

    def compile_pipeline_to_send(self, pipeline, branch):
        """
        Extract a matching build_group from the current branch name of the git repo
        then return compile the new branch matcher
        """
        matched_build_group = 'master'
        #print pipeline.get('build_group_matcher'), branch
        for key, matcher in pipeline.get('build_group_matcher').iteritems():
            m = re.search(matcher, branch)
            if m:
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

    def build(self):
        if os.path.isfile(self.wob):

            pipeline = self.get_pipeline()

            repo_dir = os.path.dirname(self.wob)

            branch = self.git_brach(repo_dir)

            send_pipeline = self.compile_pipeline_to_send(pipeline=pipeline,
                                                          branch=branch)

            self.perform(pipeline=send_pipeline)

    def deploy(self):
        if os.path.exists(self.wob):
            pipeline_yaml = open(self.wob, 'r').read()
            self.perform(pipeline_yaml=pipeline_yaml)

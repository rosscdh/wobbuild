import os
import yaml

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
GLOBAL_VARS = yaml.load(open(os.path.join(BASE_PATH, 'application.yml'), 'r').read())
GLOBAL_VARS.update({
    'BASE_PATH': BASE_PATH,
})
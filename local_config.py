import os

import utils

LOCAL_CONF_DIR = utils.get_project_path('.local_config')

def __get_key(key_name):
    if not os.path.exists(LOCAL_CONF_DIR):
        os.mkdir(LOCAL_CONF_DIR)
    
    key_path_file = os.path.join(LOCAL_CONF_DIR, key_name)
    if not os.path.exists(key_path_file):
        print(f'Authorization required. Do not have key for {key_name}.')
        path = input(f'Please enter the path for key "{key_name}":')
        with open(key_path_file, 'w') as f:
            f.write(path.strip())
    
    with open(key_path_file, 'r') as f:
        return f.read()

def get_planetlab_key():
    return __get_key('PlanetLab')

def get_prometheus_key():
    return __get_key('Prometheus')

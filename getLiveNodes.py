import argparse

import utils
import local_config


if __name__ == '__main__':
    key = local_config.get_planetlab_key()

    all_nodes = utils.collect_hostnames(utils.get_project_path('all_servers.txt'))
    successes, failures = utils.run_command(all_nodes, 'echo test', 'ubc_cpen431_5', key, timeout=3)
    for host in successes.keys():
        print(host)

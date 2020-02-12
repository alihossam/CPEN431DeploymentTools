import argparse

import utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload files to multiple nodes.')
    parser.add_argument('key', type=str, help=f'path of your planet lab ssh key, make sure your key is not password encrypted')
    args = parser.parse_args()

    all_nodes = utils.collect_hostnames(utils.get_project_path('all_servers.txt'))
    successes, failures = utils.run_command(all_nodes, 'echo test', 'ubc_cpen431_5', args.key, timeout=3)
    for host in successes.keys():
        print(host)

import argparse

import utils
import local_config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='See all live PlanetLab nodes.')
    parser.add_argument('-v', '--verbose', help='Print errors', action='store_true')
    args = parser.parse_args()

    key = local_config.get_planetlab_key()

    all_nodes = utils.collect_hostnames(utils.get_project_path('all_servers.txt'))
    successes, failures = utils.run_command(all_nodes, 'echo test', 'ubc_cpen431_5', key, timeout=5)
    if args.verbose:
        fmt_len = max((len(h) for h in failures.keys()))
        for host, stderr in failures.items():
            print(f'ERROR [{host+" "*(fmt_len-len(host))}] {stderr}'.strip())
        print('\nLIVE NODES:')

    for host in successes.keys():
        print(host)

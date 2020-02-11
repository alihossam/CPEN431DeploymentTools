import sys
import argparse
import os
from pssh.clients import ParallelSSHClient

import utils

ALL_SERVERS_PATH = utils.get_project_path('all_servers.txt')
PROMETHEUS_HOSTNAME = 'ec2-15-222-1-199.ca-central-1.compute.amazonaws.com'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload files to multiple nodes.')
    parser.add_argument('key', type=str, help=f'path of your planet lab ssh key, make sure your key is not password encrypted and your key has a public key on {PROMETHEUS_HOSTNAME}')
    args = parser.parse_args()
    print('WARNING!!! THIS SCRIPT IS NOT DONE!!!\n\n\n')

    hostnames = utils.collect_hostnames(ALL_SERVERS_PATH)
    successes, fails = utils.run_command(hostnames, 'netstat -nlp', 'ubc_cpen431_5', args.key)

    for host, stderr in fails.items():
        print(f'FAIL {host}: {stderr.strip()}')

    node_exporter_urls = []
    jmx_exporter_urls = []
    for host, stdout in successes.items():
        print('SUCCESS:', host)
        for line in stdout.split('\n'):
            print(line)
            split = line.split()
            if not split or split[0] != 'tcp':
                continue
            addr, pid_progname = split[3], split[-1]
            port = addr.split(':')[-1]
            pid, progname = pid_progname.split('/')
            if progname == 'node_exporter':
                print(f'{host} is running node_exporter on {port}')
                node_exporter_urls.append(f'{host}:{port}')
            # elif progname == ''

    print('Got node_exporter_urls', node_exporter_urls)

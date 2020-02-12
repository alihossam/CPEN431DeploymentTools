import sys
import argparse
import os
import json
import threading
from pssh.clients import ParallelSSHClient

import utils
import deploy
import fileUpload

ALL_SERVERS_PATH = utils.get_project_path('all_servers.txt')
PROMETHEUS_HOSTNAME = 'ec2-15-222-1-199.ca-central-1.compute.amazonaws.com'
PROMETHEUS_DIR = '~/prometheus-2.16.0-rc.0.linux-386'
PROMETHEUS_YAML_PATH = f'{PROMETHEUS_DIR}/prometheus.yml'
PROMETHEUS_EXEC_PATH = f'{PROMETHEUS_DIR}/prometheus'
PROMETHEUS_USER = 'ubuntu'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync all nodes to Prometheus metrics server.')
    parser.add_argument('key', type=str, help=f'path of your planet lab ssh key, make sure your key is not password encrypted')
    parser.add_argument('prometheus_key', type=str, help=f'path of your Prometheus server ssh key, make sure your key is not password encrypted and your key has a public key on {PROMETHEUS_HOSTNAME}')
    args = parser.parse_args()

    hostnames = utils.collect_hostnames(ALL_SERVERS_PATH)
    successes, fails = utils.run_command(hostnames, 'netstat -nlp', 'ubc_cpen431_5', args.key)

    node_exporter_urls = []
    jmx_exporter_urls = []
    for host, stdout in successes.items():
        for line in stdout.split('\n'):
            split = line.split()
            if not split or split[0] != 'tcp':
                continue
            addr, pid_progname = split[3], split[-1]
            port = addr.split(':')[-1]
            pid, progname = pid_progname.split('/')
            if progname == 'node_exporter':
                node_exporter_urls.append(f'{host}:{port}')
            elif progname == deploy.DEFAULT_PROC_NAME:
                jmx_exporter_urls.append(f'{host}:{port}')

    print('Got node_exporter_urls', node_exporter_urls)
    print('Got jmx_exporter_urls', jmx_exporter_urls)

    yaml_config = f"""
global:
  scrape_interval: 60s

scrape_configs:
- job_name: node
  static_configs:
  - targets: {json.dumps(node_exporter_urls)}
- job_name: jmx
  static_configs:
  - targets: {json.dumps(jmx_exporter_urls)}
- job_name: prometheus
  static_configs:
  - targets: ["localhost:9090"]
"""

    temp_file_path = utils.get_project_path('temporary_config.yaml')
    with open(temp_file_path, 'w') as f:
        f.write(yaml_config)
    
    output = utils.run_command(
        [PROMETHEUS_HOSTNAME],
        f'rm -f {PROMETHEUS_YAML_PATH}',
        PROMETHEUS_USER,
        args.prometheus_key.strip())
    successes, fails = fileUpload.upload_file_no_pssh(
        [PROMETHEUS_HOSTNAME],
        args.prometheus_key.strip(),
        temp_file_path,
        PROMETHEUS_YAML_PATH,
        user=PROMETHEUS_USER,
        verbose=False)
    os.remove(temp_file_path)


    output = utils.run_command(
        [PROMETHEUS_HOSTNAME],
        f'cd {PROMETHEUS_DIR} && killall ./prometheus',
        PROMETHEUS_USER,
        args.prometheus_key.strip())

    print('Starting Prometheus server')
    # The command to start the server hangs if successful, if the timer goes off, that means the server was started (since the command is hanging)
    def kill():
        print('Server started successfully. Exit this prompt with CTRL+C.')
        exit(0)
    threading.Timer(5, kill).start()
    utils.run_command(
        [PROMETHEUS_HOSTNAME],
        f'cd {PROMETHEUS_DIR} && ./prometheus --config.file=prometheus.yml > ~/prometheus.log 2>&1 &',
        PROMETHEUS_USER,
        args.prometheus_key.strip())

    # If the command doesnt hang we have failed to start Prometheus
    print('Failed to start server')
    exit(1)

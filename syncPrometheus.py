import sys
import argparse
import os
import json
import threading
from pssh.clients import ParallelSSHClient

import utils
import deploy
import fileUpload
import local_config

ALL_SERVERS_PATH = utils.get_project_path('all_servers.txt')
PROMETHEUS_HOSTNAME = 'ec2-15-222-1-199.ca-central-1.compute.amazonaws.com'
PROMETHEUS_DIR = '~/prometheus-2.16.0-rc.0.linux-386'
PROMETHEUS_YAML_PATH = f'{PROMETHEUS_DIR}/prometheus.yml'
PROMETHEUS_EXEC_PATH = f'{PROMETHEUS_DIR}/prometheus'
PROMETHEUS_USER = 'ubuntu'

if __name__ == '__main__':
    key = local_config.get_planetlab_key()
    prometheus_key = local_config.get_prometheus_key()

    hostnames = utils.collect_hostnames(ALL_SERVERS_PATH)
    successes, fails = utils.run_command(hostnames, 'netstat -nlp', 'ubc_cpen431_5', key)

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
        prometheus_key)
    successes, fails = fileUpload.upload_file_no_pssh(
        [PROMETHEUS_HOSTNAME],
        prometheus_key,
        temp_file_path,
        PROMETHEUS_YAML_PATH,
        user=PROMETHEUS_USER,
        verbose=False)
    os.remove(temp_file_path)


    output = utils.run_command(
        [PROMETHEUS_HOSTNAME],
        f'cd {PROMETHEUS_DIR} && killall ./prometheus',
        PROMETHEUS_USER,
        prometheus_key)

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
        prometheus_key)

    # If the command doesnt hang we have failed to start Prometheus
    print('Failed to start server')
    exit(1)

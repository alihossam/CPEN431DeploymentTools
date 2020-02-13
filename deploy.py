import sys
import argparse
from pssh.clients import ParallelSSHClient
from pssh.utils import load_private_key
import subprocess

import utils
import local_config
import fileUpload
import setupServer

DEFAULT_PROC_NAME = '431server'
DEFAULT_JAR_PATH = '~/server.jar'
DEFAULT_PORT = '1337'
DEFAULT_JAVAAGENT_PORT = '8200'


def stop_cmd():
	parser = argparse.ArgumentParser(description='Start server in multiple nodes.')
	parser.add_argument('--servers', type=str, help='path of the servers list file', required=True)
	args = parser.parse_args(sys.argv[2:])

	key = local_config.get_planetlab_key()
	hosts = utils.collect_hostnames(args.servers)
	client = ParallelSSHClient(hosts, user='ubc_cpen431_5', pkey=key, allow_agent=False)
	stop_all(client)


def start_cmd():
	parser = argparse.ArgumentParser(description='Start server in multiple nodes.')
	parser.add_argument('--servers', type=str, help='path of the servers list file', required=True)
	parser.add_argument('--jar', type=str, help='path to local JAR file to upload')
	args = parser.parse_args(sys.argv[2:])
	key = local_config.get_planetlab_key()
	hosts = utils.collect_hostnames(args.servers)
	client = ParallelSSHClient(hosts, user='ubc_cpen431_5', pkey=key, allow_agent=False)

	if args.jar:
		fileUpload.upload_file_no_pssh(hosts, key, args.jar, DEFAULT_JAR_PATH)
	start(client)


def stop_all(client):
	# TODO add checks to see if command failed by parsing output
	client.run_command(f'pkill -f {DEFAULT_PROC_NAME}')


def start(client):
	# TODO add checks to see if command failed by parsing output
	javaagent_jar_path = setupServer.get_server_config_path('jmx_prometheus_javaagent-0.12.0.jar')
	javaagent_conf_path = setupServer.get_server_config_path('javaagent_config.yml')
	cmd = f'exec -a {DEFAULT_PROC_NAME} java -javaagent:{javaagent_jar_path}={DEFAULT_JAVAAGENT_PORT}:{javaagent_conf_path} -Xmx64m -XX:+UseSerialGC -jar {DEFAULT_JAR_PATH} {DEFAULT_PORT} &'
	print('starting server with cmd:', cmd)
	output = client.run_command(cmd)
	utils.print_pssh_output(output)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Start/Stop server in multiple nodes or upload an executable.')
	parser.add_argument('action', help='start/stop server or upload a JAR file', choices=["start", "stop"])
	args = parser.parse_args(sys.argv[1:2])
	if args.action == 'start':
		start_cmd()
	else:
		stop_cmd()

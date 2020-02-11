import sys
import argparse
from pssh.clients import ParallelSSHClient
from pssh.utils import load_private_key
import subprocess
import utils

DEFAULT_PROC_NAME = '431server'
DEFAULT_JAR_PATH = '~/server/server.jar'
DEFAULT_PORT = '1337'


def run_cmds(args):
	hosts = utils.collect_hostnames(args.servers)
	client = ParallelSSHClient(hosts, user='ubc_cpen431_5', pkey=args.key, allow_agent=False)
	if args.startstop == "start":
		start(client)
	else:
		stop_all(client)


def stop_all(client):
	# TODO add checks to see if command failed by parsing output
	output = client.run_command(f'pkill -f {DEFAULT_PROC_NAME}')
	print(output)


def start(client):
	# TODO add checks to see if command failed by parsing output
	output = client.run_command(f'exec -a {DEFAULT_PROC_NAME} java -Xmx64m -jar {DEFAULT_JAR_PATH} {DEFAULT_PORT} &')
	print(output)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Start/Stop server in multiple nodes.')
	parser.add_argument('servers', type=str, help='path of the servers list file')
	parser.add_argument('key', type=str, help='path of your planet lab ssh key, make sure your key is not password encrypted')
	parser.add_argument('startstop', help='start or stop server. Pass in -start or -stop', choices=["start", "stop"])
	args = parser.parse_args()
	run_cmds(args)

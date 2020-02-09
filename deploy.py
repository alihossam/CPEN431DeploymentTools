import sys
import argparse
from pssh.clients import ParallelSSHClient
from pssh.utils import load_private_key
from gevent import joinall
import subprocess

default_proc_name = '431server'
default_jar_path = '~/server/server.jar'
default_port = '1337'

def collect_hostnames(filename):
	print('# Collecting hostnames from servers list')
	f = open(filename, 'r')
	hosts = f.readlines()
	strippedHosts = []
	for host in hosts:
		strippedHosts.append(host.strip())
	f.close()
	print('# Done collecting!')
	return strippedHosts


def run_cmds(args):
	hosts = collect_hostnames(args.servers)
	client = ParallelSSHClient(hosts, user='ubc_cpen431_5', pkey=args.key, allow_agent=False)
	if args.startstop == "start":
		start(client)
	else:
		stop_all(client)

def stop_all(client):
	# TODO add checks to see if command failed by parsing output
	output = client.run_command(f'pkill -f {default_proc_name}')

def start(client):
	# TODO add checks to see if command failed by parsing output
	output = client.run_command(f'exec -a {default_proc_name} java -Xmx64m -jar {default_jar_path} {default_port} &')


def main():
	parser = argparse.ArgumentParser(description='Start/Stop server in multiple nodes.')
	parser.add_argument('servers', type=str, help='path of the servers list file')
	parser.add_argument('key', type=str, help='path of your planet lab ssh key, make sure your key is not password encrypted')
	parser.add_argument('startstop', help='start or stop server. Pass in -start or -stop', choices=["start", "stop"])
	args = parser.parse_args()
	run_cmds(args)

main()


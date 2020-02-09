import sys
import argparse
import subprocess
import ntpath
from pssh.clients import ParallelSSHClient
from pssh.utils import load_private_key
from gevent import joinall
from pssh.utils import enable_host_logger

def collectHostnames(filename):
	print('# Collecting hostnames from servers list')
	f = open(filename, 'r')
	hosts = f.readlines()
	strippedHosts = []
	for host in hosts:
		strippedHosts.append(host.strip())
	f.close()
	print('# Done collecting!')
	return strippedHosts


# make a subprocess per host to upload -> spawns multiple scp processes
# - kept here just in case but not used in this program
def scpLoop(args):
	print("# Uploading files")
	hosts = collectHostnames(args.servers)
	procs = []
	for host in hosts:
		entry = {}
		entry['host'] = host
		cmd = getCommand(host, args)
		entry['proc'] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		procs.append(entry)

	for entry in procs:
		proc = entry['proc']
		proc.wait()
		ret = proc.poll()
		if ret != 0:
			host = entry['host']
			print(f'Uploading to host: {host} failed, scp returned code: {ret}')
	print("# Done")

def getCommand(host, args):
	return f'scp -v -i {args.key} {args.file} ubc_cpen431_5@{host}:{args.destination}'


def useSCP(args):
	enable_host_logger()
	hosts = collectHostnames(args.servers)
	client = ParallelSSHClient(hosts, user='ubc_cpen431_5', pkey=args.key, allow_agent=False)
	cmds = client.scp_send(args.file, args.destination)
	joinall(cmds, raise_error=True)
	for index, job in enumerate(cmds):
		if not job.successful():
			print(f'Failure detected: most probably host {hosts[index]}')



def main():
	parser = argparse.ArgumentParser(description='Upload files to multiple nodes.')
	parser.add_argument('servers', type=str, help='path of the servers list file')
	parser.add_argument('key', type=str, help='path of your planet lab ssh key, make sure your key is not password encrypted')
	parser.add_argument('file', type=str, help='path of the file to upload')
	parser.add_argument('destination', type=str, help='path of the file to upload. Write the path including the file name i.e. ~/dir/filename')
	

	args = parser.parse_args()
	useSCP(args)


main()


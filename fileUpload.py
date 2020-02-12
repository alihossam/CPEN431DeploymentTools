import sys
import argparse
import subprocess
import ntpath
from pssh.clients import ParallelSSHClient
from pssh.utils import load_private_key
from gevent import joinall
from pssh.utils import enable_host_logger
import utils


# make a subprocess per host to upload -> spawns multiple scp processes
# - kept here just in case but not used in this program
def upload_file_no_pssh(hosts, key, file, destination, user='ubc_cpen431_5', verbose=True):
	# procs = []
	# for host in hosts:
	# 	entry = {}
	# 	entry['host'] = host
	# 	cmd = f'scp -v -i {key} {file} {user}@{host}:{destination}'
	# 	entry['proc'] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	# 	procs.append(entry)

	# for entry in procs:
	# 	proc = entry['proc']
	# 	proc.wait()
	# 	ret = proc.poll()
	# 	if ret != 0:
	# 		host = entry['host']
	# 		print(f'Uploading to host: {host} failed, scp returned code: {ret}')
	
	verbose_flag = '-v' if verbose else ''
	commands = [f'scp {verbose_flag} -i {key} {file} {user}@{host}:{destination}' for host in hosts]
	print(commands)
	return utils.parallelize_commands(commands)


def getCommand(host, key, file, destination):
	return f'scp -v -i {key} {file} ubc_cpen431_5@{host}:{destination}'


def useSCP(args):
	enable_host_logger()
	hosts = utils.collect_hostnames(args.servers)
	client = ParallelSSHClient(hosts, user='ubc_cpen431_5', pkey=args.key, allow_agent=False)
	upload_file(client, args.file, args.destination)


def upload_file(client, local_path, destination_path):
	print(f'uploading {local_path} to {destination_path}')
	cmds = client.scp_send(local_path, destination_path)
	print('after send')
	joinall(cmds, raise_error=True)
	print('after joinall')
	for index, job in enumerate(cmds):
		if not job.successful():
			print(f'Failure detected: job index={index}')
			print(job)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Upload files to multiple nodes.')
	parser.add_argument('servers', type=str, help='path of the servers list file')
	parser.add_argument('key', type=str, help='path of your planet lab ssh key, make sure your key is not password encrypted')
	parser.add_argument('file', type=str, help='path of the file to upload')
	parser.add_argument('destination', type=str, help='path of the file to upload. Write the path including the file name i.e. ~/dir/filename')
	

	args = parser.parse_args()
	useSCP(args)

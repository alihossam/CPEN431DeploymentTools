import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

def collect_hostnames(filename):
	print('# Collecting hostnames from servers list')
	with open(filename, 'r') as f:
		return [host.strip() for host in f.readlines()]

def get_project_path(filename):
    return os.path.join(PROJECT_ROOT, filename)

def print_pssh_output(output):
    for node, result in output.items():
        for line in result.stdout:
            print(f'[{node}] {line}')

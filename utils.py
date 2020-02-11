import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))


def collect_hostnames(filename):
	with open(filename, 'r') as f:
		return [host.strip() for host in f.readlines()]


def get_project_path(filename):
    return os.path.join(PROJECT_ROOT, filename)


def print_pssh_output(output):
    for node, result in output.items():
        for line in result.stdout:
            print(f'[{node}] {line}')


def run_commands(hosts, commands, user, key, timeout=3):
    ssh_commands = [f"""ssh -l {user} -i {key} -o ConnectTimeout={timeout} {host} '{cmd}'""" for host, cmd in zip(hosts, commands)]
    procs = {
        host: subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        for host, ssh_cmd in zip(hosts, ssh_commands)
    }

    successes, fails = {}, {}

    for host, proc in procs.items():
        proc.wait()
        ret = proc.poll()
        stdout, stderr = proc.communicate()
        if ret != 0:
            fails[host] = stderr.decode('utf-8')
        else:
            successes[host] = stdout.decode('utf-8')

    return successes, fails


def run_command(hosts, command, user, key, timeout=3):
    return run_commands(hosts, [command]*len(hosts), user, key, timeout=timeout)

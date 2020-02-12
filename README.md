# CPEN431DeploymentTools

File upload and deployment scripts to automate starting and stopping scripts.

To use these tools you must have SSH and SCP installed in your command line and run
```
pip install -r requirements.txt
```


## Setting up a new node
To install Java + monitoring software on a node run:
```
python3 setupServer.py planetlab.hostname.com path/to/plab_ssh_key
```
Note that running this command will alter `all_servers.txt` so remember to commit
those changes.


## Syncing nodes with Prometheus
To sync nodes with Prometheus so that all nodes upload their metrics run:
```
python3 syncPrometheus.py path/to/plab_ssh_key path/to/prometheus_ssh_key
```

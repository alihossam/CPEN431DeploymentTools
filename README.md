# CPEN431DeploymentTools

File upload and deployment scripts to automate starting and stopping scripts.

To use these tools you **must have SSH and SCP** installed in your command line and run
```
pip install -r requirements.txt
```

The first time you run these scripts you will be prompted to enter the paths to your SSH private keys. Example:
```
Authorization required. Do not have key for PlanetLab.
Please enter the path for key "PlanetLab":~/.ssh/plab
Authorization required. Do not have key for Prometheus.
Please enter the path for key "Prometheus":~/.ssh/prometheus
```
You can change these at any time by either deleting the .local_conf directory or changing the files
inside of the .local_conf directory.


## Setting up a new node
To install Java + monitoring software on a node run:
```
python3 setupServer.py planetlab.hostname.com
```
Note that running this command will alter `all_servers.txt` so remember to commit
those changes.


## Syncing nodes with Prometheus
To sync nodes with Prometheus so that all nodes upload their metrics run:
```
python3 syncPrometheus.py
```

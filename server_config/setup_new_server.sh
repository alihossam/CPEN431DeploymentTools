# Install Java if not installed
which java
if [[ $? != 0 ]]; then
    sudo rpm -ivh ~/server_config/jre-8u31-linux-i586.rpm
fi

# Install Prometheus node_exporter
rm -rf node_exporter
if [[ $(uname --m) == 'i686' ]]; then
    tar -xzf ~/server_config/node_exporter-0.18.1.linux-386.tar.gz
    mv node_exporter-0.18.1.linux-386 node_exporter
else
    # Assume x86-64 if not i686
    tar -xzf ~/server_config/node_exporter-0.18.1.linux-amd64.tar.gz
    mv node_exporter-0.18.1.linux-amd64 node_exporter
fi

cd node_exporter
# TODO set port number dynamically
./node_exporter --web.listen-address=":48100" > ~/node_exporter.log 2>&1 &

cd ..
cp ~/server_config/node_exporter_config.yaml ./config.yaml
# java -javaagent:~/server_config/jmx_prometheus_javaagent-0.12.0.jar=[jmx_exporter port number]:config.yaml -Xmx64m -jar [your Java server].jar

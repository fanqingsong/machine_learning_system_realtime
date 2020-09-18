


# run zookeeper
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties &
cd -


# while ! nc -z localhost 2181; do
#     echo "waiting for zookeeper started"
#     sleep 1s;
# done
sleep 10s


# run kafka
rm -rf /tmp/kafka-logs/*
cd /usr/local/kafka
bin/kafka-server-start.sh config/server.properties
cd -






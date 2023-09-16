# start kafka server
KAFKA_CLUSTER_ID="$(./kafka_2.12-3.5.1/bin/kafka-storage.sh random-uuid)"
./kafka_2.12-3.5.1/bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c ./kafka_2.12-3.5.1/config/kraft/server.properties
./kafka_2.12-3.5.1/bin/kafka-server-start.sh ./kafka_2.12-3.5.1/config/kraft/server.properties

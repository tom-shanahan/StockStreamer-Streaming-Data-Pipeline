# start kafka server
KAFKA_CLUSTER_ID="$(./kafka_2.12-3.5.1/bin/kafka-storage.sh random-uuid)"
./kafka_2.12-3.5.1/bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c ./kafka_2.12-3.5.1/config/kraft/server.properties
./kafka_2.12-3.5.1/bin/kafka-server-start.sh ./kafka_2.12-3.5.1/config/kraft/server.properties

# create kafka topics
./kafka_2.12-3.5.1/bin/kafka-topics.sh --create --topic stockPrices --bootstrap-server localhost:9092
./kafka_2.12-3.5.1/bin/kafka-topics.sh --create --topic redditComments --bootstrap-server localhost:9092 
./kafka_2.12-3.5.1/bin/kafka-topics.sh --create --topic redditSubmissions --bootstrap-server localhost:9092 

# start producers
python3 /home/tshanahan/StockStreamer/stock_price_producer/stock_price_producer.py &
python3 /home/tshanahan/StockStreamer/comment_submission_producer/comment_submission_producer.py

# check kafka
kafka_2.12-3.5.1/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic stockPrices 

# start KafkaStreamToHDFS
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0 ./BatchProcessing/KafkaStreamToHDFS.py 


####

# # START CASSANDRA
# docker pull cassandra:latest
# docker network create cassandra
# docker run --rm -d --name cassandra --hostname cassandra --network cassandra cassandra
# docker run --rm --network cassandra -v "$(pwd)/cassandra/cassandra-setup.cql:/scripts/cassandra-setup.cql" -e CQLSH_HOST=cassandra -e CQLSH_PORT=9042 -e CQLVERSION=3.4.6 nuvo/docker-cqlsh


# # docker run --rm --network cassandra -v "$(pwd)/data.cql:/scripts/data.cql" -e CQLSH_HOST=cassandra -e CQLSH_PORT=9042 -e CQLVERSION=3.4.6 nuvo/docker-cqlsh
# docker run --rm -it --network cassandra nuvo/docker-cqlsh cqlsh cassandra 9042 --cqlversion='3.4.6'
# # SELECT * FROM stockdata.output_data;
# # INSERT INTO store.shopping_cart (userid, item_count) VALUES ('4567', 20);
# # docker kill cassandra
# # docker network rm cassandra


# # KafkaStreamToCassandra
# spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 ./BatchProcessing/KafkaStreamToCassandra.py

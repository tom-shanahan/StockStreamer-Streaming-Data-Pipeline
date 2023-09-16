# create kafka topics
./kafka_2.12-3.5.1/bin/kafka-topics.sh --create --topic stockPrices --bootstrap-server localhost:9092
./kafka_2.12-3.5.1/bin/kafka-topics.sh --create --topic redditComments --bootstrap-server localhost:9092 
./kafka_2.12-3.5.1/bin/kafka-topics.sh --create --topic redditSubmissions --bootstrap-server localhost:9092 


# # test commands
# # describe
# ./kafka_2.12-3.5.1/bin/kafka-topics.sh --describe --topic stockPrices --bootstrap-server localhost:9092
# ./kafka_2.12-3.5.1/bin/kafka-topics.sh --describe --topic redditSubmissions --bootstrap-server localhost:9092
# ./kafka_2.12-3.5.1/bin/kafka-topics.sh --describe --topic redditComments --bootstrap-server localhost:9092

# # start producer
# ./kafka_2.12-3.5.1/bin/kafka-console-producer.sh --topic stockPrices --bootstrap-server localhost:9092

# # start consumer
# ./kafka_2.12-3.5.1/bin/kafka-console-consumer.sh --topic stockPrices --from-beginning --bootstrap-server localhost:9092
# ./kafka_2.12-3.5.1/bin/kafka-console-consumer.sh --topic redditSubmissions --from-beginning --bootstrap-server localhost:9092
# ./kafka_2.12-3.5.1/bin/kafka-console-consumer.sh --topic redditComments --from-beginning --bootstrap-server localhost:9092

# # delete topic
# ./kafka_2.12-3.5.1/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic stockPrices
# ./kafka_2.12-3.5.1/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic redditSubmissions
# ./kafka_2.12-3.5.1/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic redditComments
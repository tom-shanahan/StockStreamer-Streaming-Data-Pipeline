# https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
"""
# for command line execution
/opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.4.1 /home/tshanahan/StockStreamer/Consumers/KafkaStreamToRDD.py
"""
# for running interactive window
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.4.1 pyspark-shell'

####

from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("KafkaStreamToRDD").getOrCreate()

kafka_topics_schemas = {
    # "stockPrices": "/home/tshanahan/StockStreamer/Schemas/StockPriceSchema.avsc",
    "redditComments": "/home/tshanahan/StockStreamer/Schemas/CommentSchema.avsc",
    "redditSubmissions": "/home/tshanahan/StockStreamer/Schemas/SubmissionSchema.avsc"
}

kafkaStreamDF = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", ",".join(kafka_topics_schemas.keys())) \
    .option("startingOffsets", "earliest") \
    .load()


topic_dataframes = {}
for topic, schema in kafka_topics_schemas.items():
    avro_schema = open(schema, "r").read()

    topic_dataframes[topic] = kafkaStreamDF \
        .filter(kafkaStreamDF["topic"] == topic) \
        .select(col("key").cast("string"), from_avro(col("value"), avro_schema).alias("data"))

for topic, topic_df in topic_dataframes.items():
    output_path = f"/home/tshanahan/StockStreamer/Consumers/hadoop/data/{topic}"
    checkpoint_location = f"/home/tshanahan/StockStreamer/Consumers/hadoop/{topic}"

    query = topic_df.writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", output_path) \
        .option("checkpointLocation", checkpoint_location) \
        .start()

    query.awaitTermination()


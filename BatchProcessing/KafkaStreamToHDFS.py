# https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
# """
# # for command line execution
# /opt/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.4.1 ./Consumers/KafkaStreamToHDFS.py
# """

from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.4.1 pyspark-shell'

class KafkaStreamToHDFS:

    def __init__(self):

        self.spark = SparkSession.builder.appName("KafkaStreamToRDD").getOrCreate()

        self.kafka_schemas = {
            "stockPrices":          open("/home/tshanahan/StockStreamer/Schemas/StockPriceSchema.avsc", "r").read(),
            "redditSubmissions":    open("/home/tshanahan/StockStreamer/Schemas/SubmissionSchema.avsc", "r").read(), 
            "redditComments":       open("/home/tshanahan/StockStreamer/Schemas/CommentSchema.avsc", "r").read()
        }

        kafkaStreamDF = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", ",".join(self.kafka_schemas.keys())) \
            .option("startingOffsets", "earliest") \
            .load()


        def writeTopic(df, BatchId):

            for topic in df.select("topic").distinct().rdd.flatMap(lambda x: x).collect():

                outputPath = f"/home/tshanahan/StockStreamer/Consumers/hadoop/data/{topic}"
                checkpointLocation = f"/home/tshanahan/StockStreamer/Consumers/hadoop/{topic}"
                
                topicDf = df.filter(df["topic"] == topic) \
                    .select(col("key").cast("string"), from_avro(col("value"), self.kafka_schemas[topic]).alias("data"))

                topicDf.write \
                    .format("parquet") \
                    .option("path", outputPath) \
                    .option("checkpointLocation", checkpointLocation) \
                    .mode("append") \
                    .save()

        kafkaStreamDF.writeStream \
            .foreachBatch(writeTopic) \
            .start() \
            .awaitTermination()

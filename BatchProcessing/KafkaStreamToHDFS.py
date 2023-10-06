from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col

class KafkaStreamToHDFS:

    def __init__(self):

        self.spark = SparkSession.builder.appName("KafkaStreamToHDFS").getOrCreate()

        self.kafka_schemas = {
            "stockPrices":          open("/home/tshanahan/StockStreamer/batch_processor/StockPriceSchema.avsc", "r").read(),
            "redditSubmissions":    open("/home/tshanahan/StockStreamer/batch_processor/SubmissionSchema.avsc", "r").read(), 
            "redditComments":       open("/home/tshanahan/StockStreamer/batch_processor/CommentSchema.avsc", "r").read()
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

if __name__ == "__main__":
    Kafka_Stream_To_HDFS = KafkaStreamToHDFS()

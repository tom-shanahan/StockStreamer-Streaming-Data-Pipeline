from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col

class BatchProcessor:

    def __init__(self):

        self.spark = SparkSession.builder.appName("BatchProcessor")\
            .appName("StreamProcessor") \
            .config('spark.cassandra.connection.host', 'cassandra') \
            .config('spark.cassandra.connection.port', '9042') \
            .config('spark.cassandra.output.consistency.level','ONE') \
            .getOrCreate()

        self.kafka_schemas = {
            "stockprices":          open("src/schemas/StockPriceSchema.avsc", "r").read(),
            "redditsubmissions":    open("src/schemas/SubmissionSchema.avsc", "r").read(), 
            "redditcomments":       open("src/schemas/CommentSchema.avsc", "r").read()
        }

        kafkaStreamDF = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafkaservice:9092") \
            .option("subscribe", ",".join(self.kafka_schemas.keys())) \
            .load()

        def writeTopic(df, BatchId):

            topics = df.select("topic").distinct().rdd.flatMap(lambda x: x).collect()
            print(topics)
            print(topics)
            print(topics)
            print(topics)
            print(topics)

            for topic in topics:
                topicDf = df.filter(df["topic"] == topic) \
                    .select(col("key").cast("string"), from_avro(col("value"), self.kafka_schemas[topic]).alias("data"))

                print(topicDf.count())
                print(topicDf.count())
                print(topicDf.count())
                print(topicDf.count())
                print(topicDf.count())

                topicDf.write \
                    .option("failOnDataLoss", "false") \
                    .options(table="output_data3", keyspace=topic) \
                    .option("checkpointLocation", "/tmp/check_point/") \
                    .format("org.apache.spark.sql.cassandra") \
                    .mode("append") \
                    .save()

        kafkaStreamDF.writeStream \
            .trigger(processingTime="5 seconds") \
            .foreachBatch(writeTopic) \
            .start() \
            .awaitTermination()

if __name__ == "__main__":
    Batch_Processor = BatchProcessor()

        
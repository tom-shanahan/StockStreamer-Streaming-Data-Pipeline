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
            for topic in topics:
                if topic == 'stockprices':
                    topicDf = df.filter(df["topic"] == topic) \
                        .select(col("key").cast("string"), from_avro(col("value"), self.kafka_schemas[topic]).alias("data"))
                    
                    writeDf = topicDf.withColumn("conditions", col("data.c")) \
                        .withColumn("price", col("data.p")) \
                        .withColumn("symbol", col("data.s")) \
                        .withColumn("timestamp", col("data.t")) \
                        .withColumn("volume", col("data.v")) \
                        .drop("data", "key")
  
                    writeDf.write \
                        .option("failOnDataLoss", "false") \
                        .options(table="output_data6", keyspace=topic) \
                        .option("checkpointLocation", "/tmp/check_point/") \
                        .format("org.apache.spark.sql.cassandra") \
                        .mode("append") \
                        .save()
                else:
                    topicDf = df.filter(df["topic"] == topic) \
                        .select(col("key").cast("string"), from_avro(col("value"), self.kafka_schemas[topic]).alias("data"))

                    topicDf.write \
                        .option("failOnDataLoss", "false") \
                        .options(table="output_data6", keyspace=topic) \
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

        
import re 
from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col, udf
from pyspark.sql.types import ArrayType, StringType, DoubleType
from pandas import read_csv

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
vaderSentiment = SentimentIntensityAnalyzer()

tickers = read_csv("src/tickers.csv")
stock_tickers = tickers['ticker'].tolist()

@udf(DoubleType())
def analyzeSentiment(text):
    sentiment = vaderSentiment.polarity_scores(text)
    return sentiment['compound']

@udf(ArrayType(StringType()))
def extractTickers(submission_titles, submission_bodies):
    submission_titles_tickers = re.findall(r'\b[A-Z]{1,4}\b', submission_titles)
    submission_bodies_tickers = re.findall(r'\b[A-Z]{1,4}\b', submission_bodies)
    return list(set([ticker for ticker in submission_titles_tickers+submission_bodies_tickers if ticker in stock_tickers]))

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

        print(",".join(self.kafka_schemas.keys()))

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
                        .options(table="output_data", keyspace=topic) \
                        .option("checkpointLocation", "/tmp/check_point/") \
                        .format("org.apache.spark.sql.cassandra") \
                        .mode("append") \
                        .save()
                    
                elif topic == 'redditsubmissions':
                    topicDf = df.filter(df["topic"] == topic) \
                        .select(col("key").cast("string"), from_avro(col("value"), self.kafka_schemas[topic]).alias("data"))

                    writeDf = topicDf.withColumn("id", col("data.id")) \
                        .withColumn("name", col("data.name")) \
                        .withColumn("title", col("data.title")) \
                        .withColumn("title_sentiment_score", analyzeSentiment(topicDf["data.title"])) \
                        .withColumn("selftext", col("data.selftext")) \
                        .withColumn("selftext_sentiment_score", analyzeSentiment(topicDf["data.selftext"])) \
                        .withColumn("subreddit", col("data.subreddit")) \
                        .withColumn("upvote_ratio", col("data.upvote_ratio")) \
                        .withColumn("num_comments", col("data.num_comments")) \
                        .withColumn("score", col("data.score")) \
                        .withColumn("created_utc", col("data.created_utc")) \
                        .withColumn("submission_tickers", extractTickers(topicDf["data.title"], topicDf["data.selftext"])) \
                        .drop("data", "key")

                    writeDf.write \
                        .option("failOnDataLoss", "false") \
                        .options(table="output_data", keyspace=topic) \
                        .option("checkpointLocation", "/tmp/check_point/") \
                        .format("org.apache.spark.sql.cassandra") \
                        .mode("append") \
                        .save()
                    
                elif topic == 'redditcomments':
                    topicDf = df.filter(df["topic"] == topic) \
                        .select(col("key").cast("string"), from_avro(col("value"), self.kafka_schemas[topic]).alias("data"))

                    writeDf = topicDf.withColumn("id", col("data.id")) \
                        .withColumn("body", col("data.body")) \
                        .withColumn("body_sentiment_score", analyzeSentiment(topicDf["data.body"])) \
                        .withColumn("created_utc", col("data.created_utc")) \
                        .withColumn("subreddit", col("data.subreddit")) \
                        .withColumn("submissionid", col("data.submissionID")) \
                        .withColumn("submissiontitle", col("data.submissionTitle")) \
                        .withColumn("submissiontitle_sentiment_score", analyzeSentiment(topicDf["data.submissiontitle"])) \
                        .withColumn("submissionselftext", col("data.submissionSelfText")) \
                        .withColumn("submissionselftext_sentiment_score", analyzeSentiment(topicDf["data.submissionselftext"])) \
                        .withColumn("score", col("data.score")) \
                        .withColumn("submission_tickers", extractTickers(topicDf["data.submissiontitle"], topicDf["data.submissionselftext"])) \
                        .drop("data", "key")

                    writeDf.write \
                        .option("failOnDataLoss", "false") \
                        .options(table="output_data", keyspace=topic) \
                        .option("checkpointLocation", "/tmp/check_point/") \
                        .format("org.apache.spark.sql.cassandra") \
                        .mode("append") \
                        .save()

        kafkaStreamDF.writeStream \
            .trigger(processingTime="15 seconds") \
            .foreachBatch(writeTopic) \
            .start() \
            .awaitTermination()

if __name__ == "__main__":
    Batch_Processor = BatchProcessor()

        
import re 
from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro
from pyspark.sql.functions import col, udf, from_unixtime, lit, explode
from pyspark.sql.types import ArrayType, StringType, DoubleType, FloatType
from pandas import read_csv, DataFrame

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
vaderSentiment = SentimentIntensityAnalyzer()

tickers = read_csv("src/tickers.csv")
stock_dict = dict(zip(tickers['name'], tickers['ticker']))
stock_tickers = tickers['ticker'].tolist()

@udf(DoubleType())
def analyzeSentiment(text):
    sentiment = vaderSentiment.polarity_scores(text)
    return sentiment['compound']

@udf(ArrayType(StringType()))
def extractTickers(submission_titles, submission_bodies, subreddit_name):
    tickers_found = set()

    # Search for tickers directly; case sensitive
    submission_titles_tickers = re.findall(r'\b[A-Z]{1,4}\b', submission_titles)
    valid_tickers = [ticker for ticker in submission_titles_tickers if ticker in stock_tickers]
    tickers_found.update(valid_tickers)

    submission_bodies_tickers = re.findall(r'\b[A-Z]{1,4}\b', submission_bodies)
    valid_tickers = [ticker for ticker in submission_bodies_tickers if ticker in stock_tickers]
    tickers_found.update(valid_tickers)

    # Search for company names and make a list of paired tickers
    for name, ticker in stock_dict.items():
        text_pattern = re.compile(r'\b{}\b'.format(re.escape(name)), re.IGNORECASE)
        if re.search(text_pattern, submission_titles):
            tickers_found.add(ticker)
        if re.search(text_pattern, submission_bodies):
            tickers_found.add(ticker) 
        
        # looser search for company name in subreddit_name
        subreddit_pattern = re.compile(format(re.escape(name)), re.IGNORECASE)
        if re.search(subreddit_pattern, subreddit_name):
            tickers_found.add(ticker)

    return list(tickers_found)


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
                        .withColumn("timestamp", from_unixtime(col("data.t").cast(FloatType()) / lit(1000))) \
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
                        .withColumn("created_utc", from_unixtime(col("data.created_utc").cast(FloatType()))) \
                        .withColumn("submission_tickers", extractTickers(topicDf["data.title"], topicDf["data.selftext"], topicDf["data.subreddit"])) \
                        .drop("data", "key") 
                    
                    exploded_df = writeDf.select(
                        "*",
                        explode("submission_tickers").alias("ticker")
                    )

                    exploded_df.write \
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
                        .withColumn("created_utc", from_unixtime(col("data.created_utc").cast(FloatType()))) \
                        .withColumn("subreddit", col("data.subreddit")) \
                        .withColumn("submissionid", col("data.submissionID")) \
                        .withColumn("submissiontitle", col("data.submissionTitle")) \
                        .withColumn("submissiontitle_sentiment_score", analyzeSentiment(topicDf["data.submissiontitle"])) \
                        .withColumn("submissionselftext", col("data.submissionSelfText")) \
                        .withColumn("submissionselftext_sentiment_score", analyzeSentiment(topicDf["data.submissionselftext"])) \
                        .withColumn("score", col("data.score")) \
                        .withColumn("submission_tickers", extractTickers(topicDf["data.submissiontitle"], topicDf["data.submissionselftext"], topicDf["data.subreddit"])) \
                        .drop("data", "key")

                    exploded_df = writeDf.select(
                        "*",
                        explode("submission_tickers").alias("ticker")
                    )

                    exploded_df.write \
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

        
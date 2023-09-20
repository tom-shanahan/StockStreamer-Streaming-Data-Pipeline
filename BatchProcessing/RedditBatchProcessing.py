from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

nltk.download('vader_lexicon')
vaderSentiment = SentimentIntensityAnalyzer()


spark = SparkSession.builder.appName("RedditBatchProcessing").getOrCreate()

redditComments = spark.read.format("parquet").\
    load("/home/tshanahan/StockStreamer/BatchProcessing/hadoop/data/redditComments")

@udf(DoubleType())
def analyzeSentiment(text):
    sentiment = vaderSentiment.polarity_scores(text)
    return sentiment['compound']


result_df = redditComments.withColumn("sentiment_score", analyzeSentiment(redditComments["data.body"]))

ordered_df = result_df.orderBy("sentiment_score")
ordered_df.head(2)

result_df.tail(100)
df = redditComments.select('data.created_utc')
df.show(5)




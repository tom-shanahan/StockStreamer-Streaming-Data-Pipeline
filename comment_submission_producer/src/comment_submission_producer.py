import io
import praw
import avro.schema
import avro.io
from kafka import *
import configparser

subreddit_list = ['stocks','wallstreetbets','investing','StockMarket',
                  'traders','ValueInvesting','StockMarket','finance',
                  'Daytrading','dividends','trading', 'teslamotors',
                  'TeslaLounge', 'teslainvestorsclub','apple','amazon',
                  'disney', 'facebook', 'google','intel','Semiconductors',
                  'microsoft','Nike']

class CommentSubmissionProducer:

    def __init__(self, subreddit_list):

        self.producer = KafkaProducer(bootstrap_servers=['kafkaservice:9092'],  api_version=(0,10,2))
        self.KafkaTopicSubmissions = "redditsubmissions"
        self.KafkaTopicComments = "redditcomments"

        with open("src/schemas/CommentSchema.avsc", "rb") as schema_file:
            self.CommentSchema = avro.schema.parse(schema_file.read())

        with open("src/schemas/SubmissionSchema.avsc", "rb") as schema_file:
            self.SubmissionSchema = avro.schema.parse(schema_file.read())

        self.config = configparser.ConfigParser()
        self.config.read("secrets/credentials.ini")

        self.reddit = praw.Reddit(
            client_id=str(self.config.get('RedditCredentials', 'client_id')),
            client_secret=str(self.config.get('RedditCredentials', 'client_secret')),
            username=str(self.config.get('RedditCredentials', 'username')),
            user_agent=str(self.config.get('RedditCredentials', 'user_agent'))
        )

        self.subreddit_list = subreddit_list
        self.subreddit = self.reddit.subreddit("+".join(str(x) for x in self.subreddit_list))

        # pause_after – An integer representing the number of requests that result in no new items before this function yields None, effectively introducing a pause into the stream. A negative value yields None after items from a single response have been yielded, regardless of number of new items obtained in that response. A value of 0 yields None after every response resulting in no new items, and a value of None never introduces a pause (default: None).
        # skip_existing – When True, this does not yield any results from the first request thereby skipping any items that existed in the stream prior to starting the stream (default: False).
        self.submission_stream = self.subreddit.stream.submissions(pause_after=-1, skip_existing=True)
        self.comment_stream = self.subreddit.stream.comments(pause_after=-1, skip_existing=True)
        
        while True:
            try:
                for submission in self.submission_stream:
                    if submission is None:
                        break
                    else:

                        SubmissionData = {
                            "name": submission.name,
                            "title": submission.title,
                            "id": submission.id,
                            "selftext": submission.selftext,
                            "subreddit": str(submission.subreddit),
                            "upvote_ratio": submission.upvote_ratio,
                            "num_comments": submission.num_comments,
                            "score": submission.score,
                            "created_utc": int(submission.created_utc)
                        }

                        byteStream = io.BytesIO()
                        encoder = avro.io.BinaryEncoder(byteStream)
                        avro.io.DatumWriter(self.SubmissionSchema).write(SubmissionData, encoder)

                        self.producer.send(topic = self.KafkaTopicSubmissions, 
                                           key = str(submission.id).encode('utf-8'), 
                                           value = byteStream.getvalue())
                    
                for comment in self.comment_stream:
                    if comment is None:
                        break
                    else:

                        CommentData = {
                            "id": comment.id,
                            "body": comment.body,
                            "created_utc": int(comment.created_utc), 
                            "subreddit": str(comment.subreddit), 
                            "submissionID": comment.submission.id, 
                            "submissionTitle": comment.submission.title, 
                            "submissionSelfText": comment.submission.selftext, 
                            "score": comment.score
                        }
                        print(CommentData)
                        byteStream = io.BytesIO()
                        encoder = avro.io.BinaryEncoder(byteStream)
                        avro.io.DatumWriter(self.CommentSchema).write(CommentData, encoder)

                        self.producer.send(topic = self.KafkaTopicComments, 
                                           key = str(comment.id).encode('utf-8'), 
                                           value = byteStream.getvalue())
                                
            except BaseException as e:
                print("Exception")
                print(str(e))

if __name__ == "__main__":
    Comment_Submission_Producer = CommentSubmissionProducer(subreddit_list)
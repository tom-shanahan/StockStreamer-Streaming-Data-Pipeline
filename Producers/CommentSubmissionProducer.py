import io
import praw
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from kafka import *

class CommentSubmissionProducer:

    def __init__(self, subreddit_list):
    
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],  api_version=(0,10,2))
        self.KafkaTopicSubmissions = "redditSubmissions"
        self.KafkaTopicComments = "redditComments"

        with open("./Schemas/CommentSchema.avsc", "rb") as schema_file:
            self.CommentSchema = avro.schema.parse(schema_file.read())

        with open("./Schemas/SubmissionSchema.avsc", "rb") as schema_file:
            self.SubmissionSchema = avro.schema.parse(schema_file.read())

        self.CommentOutput = DataFileWriter(
            open("CommentOutput.avro", "wb"), 
            DatumWriter(), 
            self.CommentSchema)
        
        self.SubmissionOutput = DataFileWriter(
            open("SubmissionOutput.avro", "wb"), 
            DatumWriter(), 
            self.SubmissionSchema)

        self.reddit = praw.Reddit(
            "bot1", user_agent="bot1 user agent"
            # client_id=os.getenv("REDDIT_CLIENT_ID"),
            # client_secret=os.getenv("REDDIT_CLIENT_SECRETS"),
            # user_agent=os.getenv("REDDIT_USER_AGENT")
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
                            "subreddit": submission.subreddit.name,
                            "upvote_ratio": submission.upvote_ratio,
                            "num_comments": submission.num_comments,
                            "score": submission.score,
                            "created_utc": int(submission.created_utc)
                        }

                        byteStream = io.BytesIO()
                        encoder = avro.io.BinaryEncoder(byteStream)
                        avro.io.DatumWriter(self.SubmissionSchema).write(SubmissionData, encoder)

                        self.producer.send(topic = self.KafkaTopicSubmissions, 
                            key = submission.subreddit.name.encode('utf-8'), 
                            value = byteStream.getvalue())

                        self.SubmissionOutput.append(SubmissionData)
                    
                for comment in self.comment_stream:
                    if comment is None:
                        break
                    else:

                        CommentData = {
                            "body": comment.body,
                            "created_utc": int(comment.created_utc), 
                            "subreddit": comment.subreddit.name, 
                            "submissionID": comment.submission.id, 
                            "submissionTitle": comment.submission.title, 
                            "submissionSelfText": comment.submission.selftext, 
                            "score": comment.score
                        }

                        byteStream = io.BytesIO()
                        encoder = avro.io.BinaryEncoder(byteStream)
                        avro.io.DatumWriter(self.CommentSchema).write(CommentData, encoder)

                        self.producer.send(topic = self.KafkaTopicComments, 
                            key = comment.subreddit.name.encode('utf-8'), 
                            value = byteStream.getvalue())

                        self.CommentOutput.append(CommentData)
                                
            except BaseException as e:
                self.SubmissionOutput.close()
                self.CommentOutput.close()
                print("Exception")
                print(str(e))
                # self.subreddit = self.reddit.subreddit("+".join(str(x) for x in subreddit_list))
                # self.comment_stream = self.subreddit.stream.comments(pause_after=-1, skip_existing=True)
                # self.submission_stream = self.subreddit.stream.submissions(pause_after=-1, skip_existing=True)

        self.SubmissionOutput.close()
        self.CommentOutput.close()
        


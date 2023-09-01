import os
import praw
import avro.schema
from avro.datafile import DataFileWriter
from avro.io import DatumWriter

class CommentSubmissionProducer:

    def __init__(self, subreddit_list):
        
        self.CommentOutput = DataFileWriter(
            open("CommentOutput.avro", "wb"), 
            DatumWriter(), 
            avro.schema.parse(open("./Schemas/CommentSchema.avsc", "rb").read()))
        
        self.SubmissionOutput = DataFileWriter(
            open("SubmissionOutput.avro", "wb"), 
            DatumWriter(), 
            avro.schema.parse(open("./Schemas/SubmissionSchema.avsc", "rb").read()))

        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRETS"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
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
                        self.SubmissionOutput.append({
                            "name": submission.name,
                            "title": submission.title,
                            "id": submission.id,
                            "selftext": submission.selftext,
                            "subreddit": submission.subreddit.name,
                            "upvote_ratio": submission.upvote_ratio,
                            "num_comments": submission.num_comments,
                            "score": submission.score,
                            "created_utc": int(submission.created_utc)
                        })
                            
                for comment in self.comment_stream:
                    if comment is None:
                        break
                    else:
                        self.CommentOutput.append({
                            "body": comment.body,
                            "created_utc": int(comment.created_utc), 
                            "subreddit": comment.subreddit.name, 
                            "submissionID": comment.submission.id, 
                            "submissionTitle": comment.submission.title, 
                            "submissionSelfText": comment.submission.selftext, 
                            "score": comment.score
                        })
                                
            except BaseException as e:
                print("Exception")
                print(str(e))
                # self.subreddit = self.reddit.subreddit("+".join(str(x) for x in subreddit_list))
                # self.comment_stream = self.subreddit.stream.comments(pause_after=-1, skip_existing=True)
                # self.submission_stream = self.subreddit.stream.submissions(pause_after=-1, skip_existing=True)

        self.SubmissionOutput.close()
        self.CommentOutput.close()
        


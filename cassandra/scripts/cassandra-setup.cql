CREATE KEYSPACE IF NOT EXISTS stockprices WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use stockprices;
CREATE TABLE IF NOT EXISTS output_data (
   symbol TEXT, 
   timestamp INT, 
   price DOUBLE, 
   volume DOUBLE, 
   conditions LIST<TEXT>, 
   PRIMARY KEY (symbol, timestamp) 
);


CREATE KEYSPACE IF NOT EXISTS redditsubmissions WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditsubmissions;
CREATE TABLE IF NOT EXISTS output_data (
   id text,
   name text,
   title text,
   title_sentiment_score double,
   selftext text,
   selftext_sentiment_score double,
   subreddit text,
   upvote_ratio double,
   num_comments int,
   score int,
   created_utc int, 
   submission_tickers list<text>,
   PRIMARY KEY (id) 
);

CREATE KEYSPACE IF NOT EXISTS redditcomments WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditcomments;
CREATE TABLE IF NOT EXISTS output_data (
   id text,
   body text,
   body_sentiment_score double,
   created_utc int, 
   subreddit text, 
   submissionid text, 
   submissiontitle text, 
   submissiontitle_sentiment_score double,
   submissionselftext text, 
   submissionselftext_sentiment_score double,
   score int, 
   submission_tickers list<text>,
   PRIMARY KEY (id) 
);

CREATE KEYSPACE IF NOT EXISTS stockprices WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use stockprices;
CREATE TABLE IF NOT EXISTS output_data (
   symbol TEXT, 
   timestamp timestamp, 
   price DOUBLE, 
   volume DOUBLE, 
   conditions LIST<TEXT>, 
   PRIMARY KEY (symbol, timestamp) 
) WITH CLUSTERING ORDER BY (timestamp DESC);


CREATE KEYSPACE IF NOT EXISTS redditsubmissions WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditsubmissions;
CREATE TABLE IF NOT EXISTS output_data (
   id text,
   ticker text,
   name text,
   title text,
   title_sentiment_score double,
   selftext text,
   selftext_sentiment_score double,
   subreddit text,
   upvote_ratio double,
   num_comments int,
   score int,
   created_utc timestamp, 
   submission_tickers list<text>,
   PRIMARY KEY (ticker, created_utc, id) 
) WITH CLUSTERING ORDER BY (created_utc DESC, id ASC);

CREATE KEYSPACE IF NOT EXISTS redditcomments WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditcomments;
CREATE TABLE IF NOT EXISTS output_data (
   id text,
   ticker text,
   body text,
   body_sentiment_score double,
   created_utc timestamp, 
   subreddit text, 
   submissionid text, 
   submissiontitle text, 
   submissiontitle_sentiment_score double,
   submissionselftext text, 
   submissionselftext_sentiment_score double,
   score int, 
   submission_tickers list<text>,
   PRIMARY KEY (ticker, created_utc, id) 
) WITH CLUSTERING ORDER BY (created_utc DESC, id ASC);


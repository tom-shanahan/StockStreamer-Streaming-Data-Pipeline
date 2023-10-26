CREATE KEYSPACE IF NOT EXISTS stockprices WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use stockprices;
CREATE TABLE IF NOT EXISTS output_data6 (
   symbol TEXT, 
   timestamp INT, 
   price DOUBLE, 
   volume DOUBLE, 
   conditions LIST<TEXT>, 
   PRIMARY KEY (symbol, timestamp) 
);


CREATE KEYSPACE IF NOT EXISTS redditsubmissions WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditsubmissions;
CREATE TABLE IF NOT EXISTS output_data6 (
   key text PRIMARY KEY,
   data text 
);


CREATE KEYSPACE IF NOT EXISTS redditcomments WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditcomments;
CREATE TABLE IF NOT EXISTS output_data6 (
   key text PRIMARY KEY,
   data text 
);
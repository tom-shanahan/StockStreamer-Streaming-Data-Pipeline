CREATE KEYSPACE IF NOT EXISTS stockprices WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use stockprices;
CREATE TABLE IF NOT EXISTS output_data3 (
   key text PRIMARY KEY,
   data text 
);


CREATE KEYSPACE IF NOT EXISTS redditsubmissions WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditsubmissions;
CREATE TABLE IF NOT EXISTS output_data3 (
   key text PRIMARY KEY,
   data text 
);


CREATE KEYSPACE IF NOT EXISTS redditcommentsWITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditcomments;
CREATE TABLE IF NOT EXISTS output_data3 (
   key text PRIMARY KEY,
   data text 
);
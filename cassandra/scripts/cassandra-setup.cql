CREATE KEYSPACE IF NOT EXISTS stockdata
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use stockdata;

CREATE TABLE IF NOT EXISTS output_data (
   topic text PRIMARY KEY
);
INSERT INTO stockdata.output_data (topic) VALUES ('AAA_TEST-1234');



CREATE KEYSPACE IF NOT EXISTS redditsubmissions
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditsubmissions;

CREATE TABLE IF NOT EXISTS output_data (
   topic text PRIMARY KEY
);
INSERT INTO redditsubmissions.output_data (topic) VALUES ('BBB_TEST-1234');



CREATE KEYSPACE IF NOT EXISTS redditcomments
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use redditcomments;

CREATE TABLE IF NOT EXISTS output_data (
   topic text PRIMARY KEY
);
INSERT INTO redditcomments.output_data (topic) VALUES ('CCC_TEST-1234');

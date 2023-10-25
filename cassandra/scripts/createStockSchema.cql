CREATE KEYSPACE IF NOT EXISTS stockdata
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

use stockdata;

CREATE TABLE IF NOT EXISTS stockdatacombined (
   ticker text,
   timestamp text,
   date int,
   price double,
   tradeVolume double,
   adjClose double,
   close double,
   high double,
   low double,
   open double,
   dailyVolume float,
   PRIMARY KEY ((ticker), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

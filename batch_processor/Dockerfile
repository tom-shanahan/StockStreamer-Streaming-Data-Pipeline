FROM apache/spark-py:v3.4.0
# FROM apache/spark:3.4.0
# ARG spark_id=185

# Installing nltk and required files
# USER root
# RUN pip install nltk
# RUN HOME=/usr/local/share/ python3 -m nltk.downloader vader_lexicon
# RUN chown -R ${spark_id}:${spark_id} /usr/local/share/
# USER ${spark_id}

WORKDIR /app

COPY . .

CMD /opt/spark/bin/spark-submit --jars jars/spark-cassandra-connector-assembly_2.12-3.4.0.jar,jars/spark-cassandra-connector_2.12-3.4.0.jar,jars/spark-token-provider-kafka-0-10_2.12-3.4.0.jar,jars/commons-pool2-2.12.0.jar,jars/kafka-clients-3.4.0.jar,jars/spark-avro_2.12-3.4.0.jar,jars/spark-sql-kafka-0-10_2.12-3.4.0.jar src/batch_processor.py



# com.datastax.spark:spark-cassandra-connector_2.12:3.2.0 \
# # Check https://stackoverflow.com/a/69559038/12382622
# CMD spark-submit \
#     --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,\
#         org.apache.kafka:kafka-clients:3.5.0,\
#         org.apache.spark:spark-avro_2.12:3.5.0 \
#     batch_processor.py


    # --conf spark.driver.extraJavaOptions="-Divy.cache.dir=/tmp -Divy.home=/tmp" \


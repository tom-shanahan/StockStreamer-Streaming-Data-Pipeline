FROM apache/spark-py:v3.4.0
ARG spark_id=185

USER root

WORKDIR /app
COPY . .

# Install Python dependencies for the application
RUN pip install --user -r requirements.txt

RUN [ "python3", "-c", "import nltk; nltk.download('vader_lexicon', download_dir='/usr/local/nltk_data')" ]

# CMD for spark-submit
CMD [ \
  "/opt/spark/bin/spark-submit", \
  "--jars", \
  "jars/spark-cassandra-connector-assembly_2.12-3.4.0.jar,jars/spark-cassandra-connector_2.12-3.4.0.jar,jars/spark-token-provider-kafka-0-10_2.12-3.4.0.jar,jars/commons-pool2-2.12.0.jar,jars/kafka-clients-3.4.0.jar,jars/spark-avro_2.12-3.4.0.jar,jars/spark-sql-kafka-0-10_2.12-3.4.0.jar", \
  "src/spark_structured_streaming.py" \
]

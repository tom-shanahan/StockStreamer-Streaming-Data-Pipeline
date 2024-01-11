# Stock Price – Reddit Sentiment Data Pipeline #

The Stock Price – Reddit Sentiment Data Pipeline is a streaming data pipeline that collects and processes data from the Finnhub.io and Reddit APIs. This is intended only as a demonstrative project, but it could be used analyze the real-time impact of Reddit comments on stock prices. 

## Architecture ##

**[[Insert diagram]]**

The above diagram visualizes the pipeline’s structure. The components are containerized into Docker containers. These containers are orchestrated by Kubernetes, with infrastructure managed by Terraform. 

1. **Data Ingestion:** Data is ingested from the Finnhub.io and Reddit APIs by two containerized Python applications, stock_price_producer.py and comment_submission_producer.py. These both receive messages from their respective sources and encode the messages into Avro format. Avro was chosen for its compact and fast binary data format its support of evolutionary schemas. The encoded messages are sent to the Kafka broker.

2. **Message Broker:** Messages from the two producers are received by the Kafka broker (kafkaservice). Messages are grouped by topics, which are initiated by a separated container kafkainit. The metadata for Kafka is managed by Zookeeper. Kafka was chosen for its scalability and reliability. 

3. **Stream Processing:** Data from the Kafka broker is consumed and processed by a Spark application run on the Kubernetes cluster. The PySpark application spark_structured_streaming.py. Consumes the data and processes it. For the Reddit data, the titles and content of the Reddit messages are analyzed for their sentiment and any ticker relevant symbols are extracted. The processed data is them written to Cassandra. Spark was chosen for this role for its scalability and ability to handle high-throughput.

4. **Data Storage:** The processed data is stored in a Cassandra cluster. The keyspaces and tables for the data are created by another container, cassandrainit. Cassandra was chosen for its Scalability and Reliability. 

5. **Visualizations:** Grafana is used to visualize the processed data stored in the Cassandra cluster. The dashboard displays…

## Deployment ##

The application is created on and designed to be deployed on a local Minikube cluster. It should be possible to deploy it on another managed Kubernetes service with minimal updates. 

Before deploying, the credentials.cfg file needs to be updated with Reddit developer credentials and a Finnhub API token. Once the credential has been updated, Minikube and Terraform can be initiated: 

```
minikube delete
minikube start --no-vtx-check --memory 4000mb --cpus 4

docker-compose build 

cd terraform-k8s
terraform init
terraform apply -auto-approve 
```

The setup progress can be monitored with the following command:

```
watch -n 1 kubectl get pods -n data-pipeline
```

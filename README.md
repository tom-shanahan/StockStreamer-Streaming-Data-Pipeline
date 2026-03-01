# Stock Price – Reddit Sentiment Data Pipeline #

A real-time streaming data pipeline built to explore the relationship between Reddit community sentiment and live stock prices. Inspired by the meme stock era and the growing influence of retail investor communities on financial markets, this project ingests data from two live APIs, processes it in real time, and visualizes the results on a live dashboard.

Built as a personal project to explore end-to-end streaming architecture using Kafka, PySpark, Terraform, and Kubernetes.

![dashboard_screenshot](https://raw.githubusercontent.com/tom-shanahan/StockStreamer-Streaming-Data-Pipeline/development/images/screenshot3.gif)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, Finnhub.io API, Reddit API, Apache Kafka, Avro |
| Stream Processing | Apache Spark (PySpark Structured Streaming) |
| Storage | Apache Cassandra |
| Infrastructure | Terraform, Kubernetes (Minikube), Docker |
| Visualization | Grafana |

---

## Architecture

![architecture_diagram](https://raw.githubusercontent.com/tom-shanahan/StockStreamer-Streaming-Data-Pipeline/development/images/architecture_diagram.jpg)

The pipeline is composed of containerized services orchestrated by Kubernetes, with infrastructure defined and managed via Terraform.

### 1. Data Ingestion
Two containerized Python applications — `stock_price_producer.py` and `comment_submission_producer.py` — ingest data from the Finnhub.io and Reddit APIs respectively. Messages are encoded in **Avro format**, chosen for its compact binary representation and support for schema evolution, then published to the Kafka broker.

### 2. Message Broker
A **Kafka** broker (`kafkaservice`) receives messages from both producers, organized by topic. Topics are initialized by a dedicated `kafkainit` container, and Kafka metadata is managed by Zookeeper. Kafka was selected for its durability, horizontal scalability, and proven reliability in high-throughput streaming systems.

### 3. Stream Processing
A **PySpark Structured Streaming** application (`spark_structured_streaming.py`) consumes messages from Kafka and processes them in real time. For Reddit data, the application performs sentiment analysis on post titles and body text, and extracts any referenced stock ticker symbols. Processed records are written to Cassandra. Spark was chosen for its ability to handle high-throughput, low-latency stream processing at scale.

### 4. Data Storage
Processed data is persisted in a **Cassandra** cluster. Keyspaces and tables are initialized by a `cassandrainit` container on startup. Cassandra's partition key design was optimized for the specific query patterns used by the Grafana dashboard, ensuring fast reads at scale.

### 5. Visualization
A **Grafana** dashboard reads from Cassandra and displays real-time stock prices alongside Reddit sentiment scores, allowing side-by-side comparison of market movement and community activity.

![dashboard_gif](https://raw.githubusercontent.com/tom-shanahan/StockStreamer-Streaming-Data-Pipeline/development/images/screenshot2.gif)

---

## Deployment

The pipeline is designed to run on a local **Minikube** cluster, but can be adapted for managed Kubernetes services (GKE, EKS, AKS) with minimal configuration changes.

### Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/docs/)
- [Terraform](https://www.terraform.io/)
- [Docker](https://www.docker.com/)
- A [Reddit developer account](https://www.reddit.com/prefs/apps) and a [Finnhub API token](https://finnhub.io/)

### Setup

**1. Add credentials**

The application is created on and designed to be deployed on a local Minikube cluster. It should be possible to deploy it on another managed Kubernetes service with minimal updates. 

Before deploying, the secrets/credentials.ini file needs to be updated with Reddit developer credentials and a Finnhub API token. 
```
[RedditCredentials]
client_id=
client_secret=
password=
username=
user_agent=

[FINNHUB]
FINNHUB_TOKEN=
```

**2. Start Minikube and build containers**

```bash
minikube delete
minikube start --no-vtx-check --memory 6000mb --cpus 8

docker-compose build
```

**3. Deploy with Terraform**

```bash
cd terraform-k8s
terraform init
terraform apply -auto-approve
```

**4. Monitor pod startup**

```bash
watch -n 1 kubectl get pods -n data-pipeline
```

**5. Open the Grafana dashboard**

Get the Grafana pod name and forward the port:

```bash
kubectl get pods --namespace=data-pipeline
kubectl port-forward pod/<grafana-pod> --namespace=data-pipeline --address 127.0.0.1 3000:3000
```

Then navigate to `http://localhost:3000` and log in with:
- **Username:** `admin`
- **Password:** `admin`

---

## Future Improvements

A few things I'd change or extend with more time:

- **Managed Kubernetes**: Deploy to a cloud-managed cluster (GKE or EKS) rather than Minikube to support production-scale workloads and simplify ops.
- **KRaft mode**: Migrate Kafka from Zookeeper-based metadata management to [KRaft](https://kafka.apache.org/documentation/#kraft), which is now the recommended approach and removes the operational overhead of running Zookeeper as a separate service.
- **Schema Registry**: Introduce a dedicated Avro schema registry (e.g., Confluent Schema Registry) to centralize schema management and enable safer schema evolution across producers and consumers.
- **Airflow or Dagster orchestration**: Add a workflow orchestration layer for better observability, retry logic, and dependency management across pipeline stages.
- **CI/CD pipeline**: Add automated testing and deployment via GitHub Actions to validate infrastructure changes before applying them.
- **Improved NLP**: Replace the current sentiment model with a finance-specific model (e.g., FinBERT) for more accurate analysis of financial discourse.

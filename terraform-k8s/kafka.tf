# defines Kubernetes Deployment 
resource "kubernetes_deployment" "zookeeper" {
  metadata {
    name = "zookeeper"
    namespace = "${var.namespace}"
    labels = {
        "k8s.service" = "zookeeper"
    }
  }

  depends_on = [
    kubernetes_namespace.pipeline-namespace
  ]

  spec {
    replicas = 1

    selector {
      match_labels = {
        "k8s.service" = "zookeeper"
      }
    }

    template {
      metadata {
        labels = {
            "k8s.network/pipeline-network" = "true"
            "k8s.service" = "zookeeper"
        }
      }

      spec {
        container {
          name = "zookeeper"
          image = "confluentinc/cp-zookeeper:7.3.5"
          port {
            container_port = 2181
          }
          env {
            name = "ZOOKEEPER_CLIENT_PORT"
            value = 2181
          }
          env {
            name = "ZOOKEEPER_TICK_TIME"
            value = 2000
          }
        }

        restart_policy = "Always"
      }
    }
  }
}

# deploys kafkaservice
resource "kubernetes_deployment" "kafkaservice" {
  metadata {
    name = "kafkaservice"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "kafka"
    }
  }

  depends_on = [
    kubernetes_deployment.zookeeper, 
    kubernetes_persistent_volume.kafkavolume, 
    kubernetes_persistent_volume_claim.kafkavolume
  ]

  spec {
    replicas = 1
    selector {
      match_labels = {
        "k8s.service" = "kafka"
      }
    }

    template { 
      metadata {
        labels = {
          "k8s.network/pipeline-network" = "true"
          "k8s.service" = "kafka"
        }
      }

      spec {
        volume {
          name = "kafkavolume"
          persistent_volume_claim {
            claim_name = "kafkavolume"
          }
        }

        # main kafka service
        container {
          name = "kafkaservice"
          image = "confluentinc/cp-kafka:7.3.2"
          port {
            container_port = 9092
          }
          port {
            container_port = 29092
          }
          volume_mount {
            name = "kafkavolume"
            mount_path = "/var/data"
          }
          env {
            name = "KAFKA_ADVERTISED_LISTENERS"
            value = "PLAINTEXT://kafkaservice:9092,PLAINTEXT_INTERNAL://kafkaservice.${var.namespace}.svc.cluster.local:29092"
          }
          env {
            name = "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP"
            value = "PLAINTEXT:PLAINTEXT,PLAINTEXT_INTERNAL:PLAINTEXT"
          }
          env {
            name = "KAFKA_BROKER_ID"
            value = 1
          }
          env {
            name = "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR"
            value = 1
          }
          env {
            name = "KAFKA_TRANSACTION_STATE_LOG_MIN_ISR"
            value = 1
          }
          env {
            name = "KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR"
            value = 1
          }
          env {
            name = "KAFKA_ZOOKEEPER_CONNECT"
            value = "zookeeper:2181"
          }
        }

        # kafka instance to initialize topics
        container {
          name = "kafkainit"
          image = "confluentinc/cp-kafka:7.3.5"

          command = ["/bin/sh"]
          args = [
            "-c",
            <<-EOT
              kafka-topics --bootstrap-server kafkaservice:29092 --create --if-not-exists --topic redditcomments --replication-factor 1 --partitions 1
              kafka-topics --bootstrap-server kafkaservice:29092 --create --if-not-exists --topic stockprices --replication-factor 1 --partitions 1
              kafka-topics --bootstrap-server kafkaservice:29092 --create --if-not-exists --topic redditsubmissions --replication-factor 1 --partitions 1
              echo -e 'created topics:'
              kafka-topics --bootstrap-server kafkaservice:29092 --list
              tail -f /dev/null
            EOT
          ]
        }

        # kafdrop container to monitor kafka service
        container {
          name = "kafdrop"
          image = "obsidiandynamics/kafdrop:3.31.0"
          port {
            container_port = 19000
          }
          env {
            name = "KAFKA_BROKERCONNECT"
            value = "localhost:29092"
          }
        }
        restart_policy = "Always"
        hostname = "kafkaservice"
      }
    }
  }
}

# defines headless Kubernetes service zookeeper
resource "kubernetes_service" "zookeeper" {
  metadata {
    name = "zookeeper"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "zookeeper"
    }
  }

  depends_on = [
    kubernetes_deployment.zookeeper
  ]

  spec {
    port {
      name = "2181"
      port = 2181
      target_port = 2181
    }
    selector = {
      "k8s.service" = "zookeeper"
    }
    cluster_ip = "None"
  }
}

# defines headless Kubernetes service kafkaservice
resource "kubernetes_service" "kafkaservice" {
  metadata {
    name = "kafkaservice"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "kafka"
    }
  }

  depends_on = [
    kubernetes_deployment.kafkaservice
  ]

  spec {
    port {
      name = "9092"
      port = 9092
      target_port = 9092
    }
    port {
      name = "29092"
      port = 29092
      target_port = 29092
    }
    port {
      name = "19000"
      port = 19000
      target_port = 19000
    }
    selector = {
      "k8s.service" = "kafka"
    }
    cluster_ip = "None"
  }
}

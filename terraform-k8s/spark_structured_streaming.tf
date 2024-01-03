# defines Kubernetes Deployment 
resource "kubernetes_deployment" "sparkstructuredstreaming" {
    metadata {
        name = "sparkstructuredstreaming"
        namespace = "${var.namespace}"
        labels = {
            "k8s.service" = "sparkstructuredstreaming"
        }
    }

    depends_on = [
        kubernetes_service.commentsubmissionproducer, 
        kubernetes_service.stockpriceproducer, 
        kubernetes_service.kafkaservice, 
        kubernetes_service.cassandra
    ]

    spec {
        replicas = 1
        selector {
            match_labels = {
                "k8s.service" = "sparkstructuredstreaming"
            }
        }

        template {
            metadata {
                labels = {
                    "k8s.service" = "sparkstructuredstreaming"
                    "k8s.network/pipeline-network" = "true"
                }
            }

            spec {
                container {
                    name = "sparkstructuredstreaming"
                    image = "tshanahan/spark_structured_streaming:latest"
                    image_pull_policy = "Always"
                    env {
                        name = "KAFKA_BROKERS"
                        value = "kafkaservice.${var.namespace}.svc.cluster.local:9092"
                    }
                }
            }
        }
    }
}

# defines headless Kubernetes service sparkstructuredstreaming
resource "kubernetes_service" "sparkstructuredstreaming" {
    metadata {
        name = "sparkstructuredstreaming"
        namespace = "${var.namespace}"
        labels = {
            "k8s.service" = "sparkstructuredstreaming"
        }
    }
    depends_on = [
        kubernetes_deployment.sparkstructuredstreaming
    ]
    spec {
        selector = {
            "k8s.service" = "sparkstructuredstreaming"
        }
        cluster_ip = "None"
    }
}
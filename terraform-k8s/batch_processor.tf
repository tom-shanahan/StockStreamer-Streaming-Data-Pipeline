resource "kubernetes_deployment" "spark" {
    metadata {
        name = "spark"
        namespace = "${var.namespace}"
        labels = {
            "k8s.service" = "spark"
        }
    }

  depends_on = [
        kubernetes_service.commentsubmissionproducer, 
        kubernetes_service.cassandra
    ]

    spec {
        replicas = 1

        selector {
            match_labels = {
                "k8s.service" = "spark"
            }
        }

        template {
            metadata {
                labels = {
                    "k8s.service" = "spark"

                    "k8s.network/pipeline-network" = "true"
                }
            }

            spec {
                container {
                    name = "spark"
                    image = "tshanahan/batch_processor:latest"
                    image_pull_policy = "Always"

                    # environment variables
                    env {
                        name = "KAFKA_BROKERS"
                        value = "kafkaservice.${var.namespace}.svc.cluster.local:9092"
                    }
                }
            }
        }
    }
}

resource "kubernetes_service" "spark" {
    metadata {
        name = "spark"
        namespace = "${var.namespace}"
        labels = {
            "k8s.service" = "spark"
        }
    }
  
    depends_on = [
        kubernetes_deployment.spark
    ]

    spec {
        selector = {
            "k8s.service" = "spark"
        }

        cluster_ip = "None"
    }
}
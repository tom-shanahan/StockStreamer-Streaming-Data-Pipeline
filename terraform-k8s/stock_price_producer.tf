# defines Kubernetes Deployment 
resource "kubernetes_deployment" "stockpriceproducer" {
  metadata {
    name = "stockpriceproducer"
    namespace = "${var.namespace}"
    labels = {
        "k8s.service" = "stockpriceproducer"
    }
  }

  depends_on = [
    kubernetes_deployment.kafkaservice, 
    kubernetes_deployment.cassandra
  ]

  spec {
    replicas = 1
    selector {
      match_labels = {
        "k8s.service" = "stockpriceproducer"
      }
    }

    template {
      metadata {
        labels = {
          "k8s.service" = "stockpriceproducer"
          "k8s.network/pipeline-network" = "true"
        }
      }

      spec {
        container {
          name = "stockpriceproducer"
          image = "tshanahan/stock_price_producer:latest"
          image_pull_policy = "Always"
          volume_mount {
            name = "credentials"
            mount_path = "/app/secrets/"
            read_only = true
          }
        }

        volume {
          name = "credentials"
          secret {
            secret_name = kubernetes_secret.credentials.metadata[0].name
          }
        }
        restart_policy = "Always"
      }
    }
  }
}

# # defines headless Kubernetes service stockpriceproducer
resource "kubernetes_service" "stockpriceproducer" {
  metadata {
    name = "stockpriceproducer"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "stockpriceproducer"
    }
  }
  depends_on = [
    kubernetes_deployment.stockpriceproducer
  ]
  spec {
    selector = {
        "k8s.service" = "stockpriceproducer"
    }
    cluster_ip = "None"
  }
}
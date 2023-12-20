# defines Kubernetes Deployment 
resource "kubernetes_deployment" "commentsubmissionproducer" {
  metadata {
    name = "commentsubmissionproducer"
    namespace = "${var.namespace}"
    labels = {
        "k8s.service" = "commentsubmissionproducer"
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
        "k8s.service" = "commentsubmissionproducer"
      }
    }
    template {
      metadata {
        labels = {
          "k8s.service" = "commentsubmissionproducer"
          "k8s.network/pipeline-network" = "true"
        }
      }

      spec {
        container {
          name = "commentsubmissionproducer"
          image = "tshanahan/comment_submission_producer:latest"
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

# creates headless Kubernetes service commentsubmissionproducer
resource "kubernetes_service" "commentsubmissionproducer" {
  metadata {
    name = "commentsubmissionproducer"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "commentsubmissionproducer"
    }
  }
  
  depends_on = [
    kubernetes_deployment.commentsubmissionproducer
  ]

  spec {
    selector = {
        "k8s.service" = "commentsubmissionproducer"
    }
    cluster_ip = "None"
  }
}
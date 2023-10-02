resource "kubernetes_persistent_volume" "kafka-volume" {
  metadata {
    name = "kafka-volume"
  }

  depends_on = [
    kubernetes_namespace.pipeline-namespace
  ]

  spec {
    capacity = {
        storage = "1Gi"
    }
    access_modes = ["ReadWriteMany"]
    storage_class_name = "hostpath"
    persistent_volume_reclaim_policy = "Retain"
    persistent_volume_source {
      host_path {
        path = "/var/lib/minikube/pv0001"
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim" "kafka-volume" {
  metadata {
    name = "kafka-volume"
    namespace = "${var.namespace}"
    labels = {
        "k8s.service" = "kafka-volume"
    }
  }

  depends_on = [ kubernetes_namespace.pipeline-namespace ]

  spec {
    access_modes = ["ReadWriteMany"]
    storage_class_name = "hostpath"

    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}
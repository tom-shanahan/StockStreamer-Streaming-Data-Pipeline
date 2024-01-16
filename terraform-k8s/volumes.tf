# defines Kubernetes Persistent Volumes and Volume Claims for Kafka and Cassandra
# storage_class_name = "hostpath": uses the local node's file system for storage; useful for development/testing environments
resource "kubernetes_persistent_volume" "kafkavolume" {
  metadata {
    name = "kafkavolume"
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

resource "kubernetes_persistent_volume_claim" "kafkavolume" {
  metadata {
    name = "kafkavolume"
    namespace = "${var.namespace}"
    labels = {
        "k8s.service" = "kafkavolume"
    }
  }
  depends_on = [
    kubernetes_namespace.pipeline-namespace
  ]
  spec {
    access_modes = ["ReadWriteMany"]
    storage_class_name = "hostpath"
    resources {
      requests = {
        storage = "500Mi"
      }
    }
  }
}

resource "kubernetes_persistent_volume" "cassandravolume" {
  metadata {
    name = "cassandravolume"
  }
  depends_on = [
    kubernetes_namespace.pipeline-namespace
  ]
  spec {
    capacity = {
      storage = "5Gi"
    }
    access_modes = ["ReadWriteMany"]
    storage_class_name = "hostpath"
    persistent_volume_reclaim_policy = "Retain"
    persistent_volume_source {
      host_path {
        path = "/var/lib/minikube/pv0002/"
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim" "cassandravolume" {
  metadata {
    name = "cassandravolume"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "cassandravolume"
    }
  }

  depends_on = [
    kubernetes_namespace.pipeline-namespace
  ]

  spec {
    access_modes = ["ReadWriteMany"]
    storage_class_name = "hostpath"

    resources {
      requests = {
        storage = "500Mi"
      }
    }
  }
}
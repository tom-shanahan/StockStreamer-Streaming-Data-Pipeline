# defines Kubernetes Deployment 
resource "kubernetes_deployment" "cassandra" {
  metadata {
    name = "cassandra"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "cassandra"
    }
  }

  depends_on = [
        kubernetes_persistent_volume_claim.cassandravolume,
        kubernetes_persistent_volume.cassandravolume
  ]

  spec {
    replicas = 1

    selector {
      match_labels = {
        "k8s.service" = "cassandra"
      }
    }

    template {
      metadata {
        labels = {
          "k8s.network/pipeline-network" = "true"
          "k8s.service" = "cassandra"
        }
      }

      spec {
        hostname = "cassandra"
        restart_policy = "Always"
        volume {
          name = "cassandra-data"
          persistent_volume_claim {
            claim_name = "cassandravolume"
          }
        }

        # main cassandra service
        container {
          name  = "cassandra"
          image = "tshanahan/cassandra:latest"
          image_pull_policy = "Always"
          port {
            container_port = 9042
          }
          env {
            name  = "CASSANDRA_CLUSTER_NAME"
            value = "CassandraCluster"
          }
          env {
            name  = "CASSANDRA_DATACENTER"
            value = "DataCenter1"
          }
          env {
            name  = "CASSANDRA_ENDPOINT_SNITCH"
            value = "GossipingPropertyFileSnitch"
          }
          env {
            name  = "CASSANDRA_HOST"
            value = "cassandra"
          }
          env {
            name  = "CASSANDRA_NUM_TOKENS"
            value = "128"
          }
          env {
            name  = "CASSANDRA_RACK"
            value = "Rack1"
          }
          env {
            name  = "HEAP_NEWSIZE"
            value = "128M"
          }
          env {
            name  = "MAX_HEAP_SIZE"
            value = "256M"
          }
          env {
            name = "POD_IP"
            value_from {
              field_ref {
                field_path = "status.podIP"
              }
            }
          }
          volume_mount {
            name       = "cassandra-data"
            mount_path = "/var/lib/cassandra"
          }
        }

        # cassandra instance to initialize data tables
        container {
          name  = "cassandrainit"
          image = "tshanahan/cassandra:latest"
          image_pull_policy = "Always"
          command = [
            "/bin/sh",
            "-c",
            <<-EOF
              sleep 30 &&
              echo "creating Cassandra keyspaces/tables" &&
              cqlsh cassandra -f /cassandra-setup.cql &&
              tail -f /dev/null
            EOF
          ]
        }
      }
    }
  }
}

# defines headless Kubernetes service "cassandra" with port 9042 for Cassandra deployment
resource "kubernetes_service" "cassandra" {
  metadata {
    name = "cassandra"
    namespace = "${var.namespace}"
    labels = {
      "k8s.service" = "cassandra"
    }
  }

  depends_on = [
    kubernetes_deployment.cassandra
  ]

  spec {
    port {
      name        = "9042"
      port        = 9042
      target_port = 9042
    }

    selector = {
      "k8s.service" = "cassandra"
    }

    cluster_ip = "None"
  }
}
# creates Kubernetes namespace 
resource "kubernetes_namespace" "pipeline-namespace" {
  metadata {
    name = "${var.namespace}"
  }
}

# loads and makes available credentials
resource "kubernetes_secret" "credentials" {
    metadata {
      name = "credentials"
      namespace = "${var.namespace}"
    }
    depends_on = [ 
      kubernetes_namespace.pipeline-namespace
    ]
    data = {
      "credentials.ini" = "${file("../secrets/credentials.ini")}"
    }
}

# restricts incoming traffic to pods with the label "k8s.network/pipeline-network" 
resource "kubernetes_network_policy" "pipeline_network" {
  metadata {
    name = "pipeline-network"
    namespace = "${var.namespace}"
  }

  depends_on = [
    kubernetes_namespace.pipeline-namespace
  ]

  spec {
    pod_selector {
      match_labels = {
        "k8s.network/pipeline-network" = "true"
      }
    }

    policy_types = [
      "Ingress"
    ]

    ingress {
      from {
        pod_selector {
          match_labels = {
            "k8s.network/pipeline-network" = "true"
          }
        }
      }
    }
  }
}
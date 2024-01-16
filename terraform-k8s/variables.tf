variable "confluent_kafka_version" {
  type    = string
  default = "7.3.5"
}

variable "confluent_zookeeper_version" {
  type    = string
  default = "7.3.5"
}

variable "kube_config" {
  type = string
  default = "~/.kube/config"
}

variable "namespace" {
  type    = string
  default = "data-pipeline"
}

variable "linode_token" {
  description = "Linode API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Linode region"
  type        = string
  default     = "ap-south"
}

variable "k8s_version" {
  description = "LKE Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "node_type" {
  description = "Linode instance type for LKE nodes"
  type        = string
  default     = "g6-standard-2"
}

variable "node_count" {
  description = "Number of LKE worker nodes"
  type        = number
  default     = 2
}
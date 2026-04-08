terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
      version = "~> 2.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "linode" {
  token = var.linode_token
}

# LKE Cluster
resource "linode_lke_cluster" "speakops" {
  label       = "speakops-cluster"
  region      = var.region
  k8s_version = var.k8s_version

  pool {
    type  = var.node_type
    count = var.node_count

    autoscaler {
      min = 2
      max = 10
    }
  }

  tags = ["speakops", "production"]
}

# Linode Managed PostgreSQL
resource "linode_database_postgresql" "speakops_db" {
  label           = "speakops-db"
  region          = var.region
  engine_id       = "postgresql/16"
  cluster_size    = 1
  type            = "g6-nanode-1"
  allow_list      = ["0.0.0.0/0"]
}

# Save kubeconfig locally
resource "local_file" "kubeconfig" {
  content         = base64decode(linode_lke_cluster.speakops.kubeconfig)
  filename        = "${path.module}/kubeconfig.yaml"
  file_permission = "0600"
}
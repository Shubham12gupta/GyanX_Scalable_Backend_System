output "cluster_id" {
  description = "LKE Cluster ID"
  value       = linode_lke_cluster.speakops.id
}

output "cluster_status" {
  description = "LKE Cluster status"
  value       = linode_lke_cluster.speakops.status
}

output "db_host" {
  description = "PostgreSQL host"
  value       = linode_database_postgresql.speakops_db.host_primary
  sensitive   = true
}

output "db_port" {
  description = "PostgreSQL port"
  value       = linode_database_postgresql.speakops_db.port
}

output "kubeconfig_path" {
  description = "Path to kubeconfig"
  value       = local_file.kubeconfig.filename
}
resource "linode_firewall" "speakops_firewall" {
  label = "speakops-firewall"

  inbound_policy  = "DROP"
  outbound_policy = "ACCEPT"

  # SSH
  inbound {
    label    = "ssh"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "22"
    ipv4     = ["0.0.0.0/0"]
  }

  # HTTP
  inbound {
    label    = "http"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "80"
    ipv4     = ["0.0.0.0/0"]
  }

  # HTTPS
  inbound {
    label    = "https"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "443"
    ipv4     = ["0.0.0.0/0"]
  }

  # LKE NodePort range
  inbound {
    label    = "nodeport"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "30000-32767"
    ipv4     = ["0.0.0.0/0"]
  }
}
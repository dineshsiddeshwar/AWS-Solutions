# create VPC
resource "google_compute_network" "my_vpc" {
  name                    = "gpn-vpc"
  auto_create_subnetworks = "false"
  routing_mode            = "GLOBAL"
}
# create public subnet
resource "google_compute_subnetwork" "network_subnet" {
  name          = "gpn-subnet"
  ip_cidr_range = var.network-subnet-cidr
  network       = google_compute_network.my_vpc.name
  region        = var.gcp_region
}

# Allow http
resource "google_compute_firewall" "allow-http" {
  name    = "gpn-fw-allow-http"
  network = google_compute_network.vpc.name
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["http"] 
}

# allow ssh
resource "google_compute_firewall" "allow-ssh" {
  name    = "gpn-fw-allow-ssh"
  network = google_compute_network.vpc.name
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["http"]
}

resource "google_compute_instance" "ui_server_1" {
  name         = "rhel-vm"
  machine_type = var.linux_instance_type
  zone         = var.gcp_zone
  hostname     = "globalpayments.com"
  tags         = ["ssh","http"]
  boot_disk {
    initialize_params {
      image = var.rhel_8_sku
    }
  }
  
  #install tomcat jdk
  metadata_startup_script = "#!/bin/bash yum -y java-17.0.6-openjdk-devel yum -y install tomcat systemctl enable tomcat systemctl start tomcat echo"
  
  network_interface {
    network       = google_compute_network.vpc.name
    subnetwork    = google_compute_subnetwork.network_subnet.name
    access_config { }
  }
}
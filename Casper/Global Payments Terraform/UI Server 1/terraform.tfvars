#gcp settings
gcp_project   = "gpn-deployment"
gcp_region    = "us-east-1"
gcp_auth_file = "../../../"



# Application Definition 
company     = "gpn"
app_name    = "iac-rhel"
app_domain  = "gpn.com"
environment = "dev" # Dev, Test, Prod, etc


# GCP Netwok
network-subnet-cidr =["10.10.12.0/24",10.110] #try

# Linux VM
linux_instance_type = "f1-micro"
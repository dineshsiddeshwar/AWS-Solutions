# data "terraform_remote_state" "vpc" {
#   backend = "azurerm"
#   config = {
#     resource_group_name  = "EYGDSSEC-rg"
#     storage_account_name = "eygdssecterraformstate"
#     container_name       = "terraform-state"
#     key                  = "baseline/network/terraform.tfstate"
#   }
# }

data "azurerm_client_config" "current" {}

module "traffic_mgr" {
source              = "../Modules/traffic_mgr"
resource_group_name   = "EYGDSSECbaseline-rg"
tags = var.tags
location = var.location
profilename = var.profilename
traffic_routing = var.traffic_routing

protocol = var.protocol
port = var.port
path = var.path
interval = var.interval
timeout = var.timeout
failures = var.failures

endpointname = var.endpointname
# targeturl = var.targeturl
target_resource_id  = var.target_resource_id 
endpointtype = var.endpointtype

}
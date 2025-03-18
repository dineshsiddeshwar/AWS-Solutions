# Title: Storage accounts should use private link
# Description: Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. 
# Developer: EY
# Version: 1.0

package wiz

default result = "pass"

result = "fail" {
	count(input.properties.privateEndpointConnections) == 0
    
}

# Remediation
# Azure Private Link lets you connect your virtual network to Azure services without a public IP address at the source or destination. 
# The Private Link platform handles the connectivity between the consumer and services over the Azure backbone network. 
# By mapping private endpoints to your storage account, data leakage risks are reduced. Learn more about private links at - https://aka.ms/azureprivatelinkoverview"
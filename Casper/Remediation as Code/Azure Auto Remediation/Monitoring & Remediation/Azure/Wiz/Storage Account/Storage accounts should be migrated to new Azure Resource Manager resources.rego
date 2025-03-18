# Title:Storage accounts should be migrated to new Azure Resource Manager resources
# Description: Use new Azure Resource Manager for your storage accounts to provide security enhancements such as: stronger access control (RBAC), 
# better auditing, Azure Resource Manager based deployment and governance, access to managed identities, access to key vault for secrets, \
# Azure AD-based authentication and support for tags and resource groups for easier security management
# Developer: EY
# Version: 1.0

package wiz

default result = "pass"

result = "fail" {
	input.type == "Microsoft.ClassicStorage/storageAccounts"
}

# Remediation
# upgrade to Premium
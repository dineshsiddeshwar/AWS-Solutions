from unicodedata import name
from gql import gql

class gqlQueryAndVariable:
    def __init__(self, query:gql, variables):
        self.query=query
        self.variables=variables

createCloudConfigurationPolicy = gqlQueryAndVariable(
    gql("""
    mutation createCloudConfigurationRulePayload($input: CreateCloudConfigurationRuleInput!) {
        createCloudConfigurationRule(input: $input) {
            rule {
                name
                id
                enabled
            }
        }
    }
    """), 
    {
        "input": {
            "name": "",
            "description": "",
            "targetNativeTypes": [],
            "opaPolicy": "",
            "severity": "MEDIUM",
            "enabled": True,
            "remediationInstructions": "",
            "scopeAccountIds": [],
            "functionAsControl": False,
            "securitySubCategories": [],
            "iacMatchers": []
        }
    }
)

deleteCloudConfigurationPolicy=gqlQueryAndVariable(gql("""
    mutation deleteCloudConfigurationRule($input: DeleteCloudConfigurationRuleInput!){
    deleteCloudConfigurationRule(input: $input){
        _stub
    }
    }
"""),{})

createWizSeurityFramework= gqlQueryAndVariable(
    gql("""
        mutation createSecurityFramework($input:CreateSecurityFrameworkInput!){
        createSecurityFramework(input: $input){
            framework{
                name
                id
            }
        }
        }"""),
        {}
)
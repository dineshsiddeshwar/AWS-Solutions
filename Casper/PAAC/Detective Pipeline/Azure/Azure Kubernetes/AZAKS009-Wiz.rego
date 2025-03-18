package wiz
default result = "fail"
result = "pass" {
input.properties.addonProfiles.omsAgent.enabled == true ; 
count(input.properties.addonProfiles.omsAgent.config) > 0
}
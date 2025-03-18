
package wiz

default result := "pass"

# Check if access logs are enabled
result := "fail" {
    not access_logs_enabled
#     not albbucket
#     not internal

}
result := "fail" {
#     not access_logs_enabled
    not bucket
#     not internal

}

access_logs_enabled {
    attribute := input.loadBalancerAttributes[i]
    attribute.Key == "access_logs.s3.enabled" 
    attribute.Value == "true"
}
# 
bucket {
    attribute := input.loadBalancerAttributes[i]
    attribute.Key == "access_logs.s3.bucket" 
    #attribute.Value == "XXXXX"
    contains(attribute.Value, "XXXXX")
}


currentConfiguration := sprintf("", [])
expectedConfiguration := sprintf("Load Balancer should have access logs enabled and pointing to logging bucket ", [])
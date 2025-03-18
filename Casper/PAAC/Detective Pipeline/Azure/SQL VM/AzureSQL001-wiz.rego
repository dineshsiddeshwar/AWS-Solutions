package wiz
default result = "fail"
result = "pass" {                 
 input.properties.minimalTlsVersion == "1.2"
}
result = "pass" {                 
 input.properties.minimalTlsVersion == "1.3"
}

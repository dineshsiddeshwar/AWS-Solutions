
package wiz
default result = "fail"

result = "pass" {
   input.dbClusterParameterGroup.Parameters[_].AllowedValues == "TLSv1,TLSv1.1,TLSv1.2"
}

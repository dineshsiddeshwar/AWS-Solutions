
package wiz
default result = "pass"

result = "fail" {
   input.DeletionProtection == false
}

package wiz

default result = "fail"

result = "pass" {
   input.Resources.SGroup1.DeletionPolicy = "Retain"
}



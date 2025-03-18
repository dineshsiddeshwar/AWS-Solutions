package wiz
default result = "fail"

 result = "pass"{
  	input.BlockDeviceMappings[0].Ebs.DeleteOnTermination == false
}

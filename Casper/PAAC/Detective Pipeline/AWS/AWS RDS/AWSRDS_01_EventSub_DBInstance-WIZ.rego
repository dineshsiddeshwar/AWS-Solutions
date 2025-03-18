package wiz
default result = "fail"

 result = "pass"{
 	input.EventSubscriptionsList[1].Enabled == true
 	input.EventSubscriptionsList[1].SourceType == "db-instance"
  	
}
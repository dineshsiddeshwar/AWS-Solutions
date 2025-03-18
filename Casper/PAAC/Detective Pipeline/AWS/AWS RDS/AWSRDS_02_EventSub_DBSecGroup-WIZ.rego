package wiz

default result = "fail"

 result = "pass"{
 	input.EventSubscriptionsList[0].Enabled == true
 	input.EventSubscriptionsList[0].SourceType == "db-security-group"
  	
}

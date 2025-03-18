package wiz
 
 default result="fail"
 
 result="pass"{
               input.properties.networkInterfaces[0].id>0;
               input.properties.subnets[0].id>0            
 }
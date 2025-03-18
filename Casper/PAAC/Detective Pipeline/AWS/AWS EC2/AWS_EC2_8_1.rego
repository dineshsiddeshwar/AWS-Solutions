package wiz 
default result="fail"
result="pass"
  {
         input.BlockDeviceMappings[0].Ebs.DeleteOnTermination==true;
         input.NetworkInterfaces[0].Attachment.DeleteOnTermination==true
  }

package wiz
default result = "fail"
result = "pass" {                 
               input.DataSources.CloudTrail.Status == "ENABLED";
               input.DataSources.DNSLogs.Status == "ENABLED";
               input.DataSources.FlowLogs.Status == "ENABLED"
               input.DataSources.S3Logs.Status=="ENABLED";
               input.ThreatIntelSets.e4c04321f62a9f68008ae09d1b752735.Status=="ACTIVE"
       }

package wiz
default result = "pass"

result = "fail" {
    input.Destinations[0].ExtendedS3DestinationDescription.S3BackupMode == "Disabled"   
}
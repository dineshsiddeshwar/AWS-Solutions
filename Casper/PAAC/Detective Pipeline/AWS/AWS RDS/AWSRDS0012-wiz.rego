package wiz
default result = "fail"

result = "pass" {
   input.BackupRetentionPeriod >= 30
}

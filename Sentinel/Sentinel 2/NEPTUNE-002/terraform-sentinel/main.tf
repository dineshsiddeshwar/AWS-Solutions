resource "aws_neptune_cluster" "neptune-cluster" {
  cluster_identifier                  = "neptune-cluster-demo"
  engine                              = "neptune"
  backup_retention_period             = 5
  enable_cloudwatch_logs_exports      = ["audit"]
}
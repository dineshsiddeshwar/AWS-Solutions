resource "aws_neptune_cluster" "default" {
  engine                              = "neptune"
  skip_final_snapshot                 = true
  apply_immediately                   = true
}
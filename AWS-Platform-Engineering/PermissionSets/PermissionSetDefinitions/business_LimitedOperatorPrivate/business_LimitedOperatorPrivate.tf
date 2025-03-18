data "aws_ssoadmin_instances" "sso_instance" {}

resource "aws_ssoadmin_permission_set" "business_LimitedOperatorPrivate" {
  name             = "business_LimitedOperatorPrivate"
  instance_arn     = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  description = "Allow ability to start and stop whitelisted services"
  session_duration= "PT1H"
}


resource "aws_ssoadmin_managed_policy_attachment" "business_LimitedOperatorPrivate" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/AWSSupportAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_LimitedOperatorPrivate.arn
}

resource "aws_ssoadmin_managed_policy_attachment" "business_LimitedOperatorPrivate1" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.business_LimitedOperatorPrivate.arn
}

data "aws_iam_policy_document" "business_LimitedOperatorPrivate" {
    statement {
    sid = "Stmt1530080969830"
    effect = "Allow"
    actions = [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ecr:StartImageScan",
        "ecr:StartLifecyclePolicyPreview",
        "ecs:StartTask",
        "ecs:StopTask",
        "rds:StartDBCluster",
        "rds:StopDBCluster",
        "rds:StartExportTask",
        "rds:StartActivityStream",
        "rds:StopDBInstance",
        "rds:StartDBInstance",
        "rds:StopActivityStream",
        "dms:StartReplicationTask",
        "dms:StopReplicationTask",
        "dms:StartReplicationTaskAssessment",
        "appstream:Stop*",
        "appstream:Start*",
        "sagemaker:Start*",
        "sagemaker:Stop*",
        "athena:StartQueryExecution",
        "athena:StopQueryExecution",
        "elasticmapreduce:StartEditor",
        "elasticmapreduce:StopEditor",
        "glue:Start*",
        "glue:Stop*",
        "workspaces:startWorkspaces",
        "workspaces:stopWorkspaces",
        "workspaces:rebootWorkspaces",
        "elasticbeanstalk:RestartAppServer"            
    ]

    resources = [
      "*",
    ]
  }
}


resource "aws_ssoadmin_permission_set_inline_policy" "business_LimitedOperatorPrivate" {
  inline_policy      = file("${path.module}/policy.json")
  instance_arn       = tolist(data.aws_ssoadmin_instances.sso_instance.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.business_LimitedOperatorPrivate.arn
}
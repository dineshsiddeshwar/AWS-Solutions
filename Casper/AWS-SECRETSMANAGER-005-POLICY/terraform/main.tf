resource "aws_iam_policy" "test_policy" {
  name = "test_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "secretsmanager:ListScrets"
        Effect   = "Allow"
        Resource = ["arn:aws:secretsmanager:us-east-1:053936224785:secret:test_secret"]
      },
    ]
  })
}

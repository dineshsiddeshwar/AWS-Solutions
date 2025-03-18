resource "aws_iam_group_policy" "test_policy" {
  name = "test_policy"
  group = aws_iam_group.test_group.id
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

resource "aws_iam_group" "test_group" {
  name = "test_group"
}
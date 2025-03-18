resource "aws_iam_user_policy" "test_policy" {
  name = "test_policy"
  user = aws_iam_user.test_user.id
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

resource "aws_iam_user" "test_user" {
  name = "test_user"
}
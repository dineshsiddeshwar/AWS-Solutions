{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::${atlterraformbackendbucket}",
                "arn:aws:s3:::${atlterraformbackendbucket}/*",
                "arn:aws:dynamodb:us-east-1:${masteraccountid}:table/${atlterraformbackenddynamodb}"
            ],
            "Effect": "Allow"
        }
    ]
}
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "events:PutEvents"
            ],
            "Resource": [
                "arn:aws:events:*:${irmaccountid}:event-bus/${irmenvironment}"
            ],
            "Effect": "Allow"
        }
    ]
}
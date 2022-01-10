# Task Orchestration Platform

## Requirementes

You need a AWS IAM user with following policy attached:
```json
{
    "Id": "Policy1",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:PutObject"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::<BUCKET_NAME>",
                "arn:aws:s3:::<BUCKET_NAME>/*"
            ]
        }
    ]
}
```
You have to replace `BUCKET_NAME` with your bucket name.

- docker
- kind
- kubectl configurado
- helm
- s3 bucket
- preencher Makefile com as credenciais
- ajustar configs no yaml

## References
- https://marclamberti.com/blog/airflow-on-kubernetes-get-started-in-10-mins
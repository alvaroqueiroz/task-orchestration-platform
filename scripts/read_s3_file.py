import boto3
import awswrangler as wr

boto3.setup_default_session(profile_name='staging')

df = wr.s3.read_csv(path='s3://task-orchestration-platform/files/consumer.csv.gz', sep=',', compression='gzip')

print(df)
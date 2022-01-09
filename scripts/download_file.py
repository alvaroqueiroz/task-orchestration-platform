import boto3
import json
import argparse
import requests
import awswrangler as wr

from utils.logger import get_std_logger


logger = get_std_logger()


def download_file(file_uri, file_name, output_path):
    res = requests.get(file_uri)
    logger.info(f"Starting download file {args.file_uri} to {args.output_path}")
    
    logger.info(f"Writing file...")
    with open(f"/tmp/{file_name}", 'wb') as f:
        f.write(res.content)
        
    logger.info(f"Uploading file to s3")
    wr.s3.upload(local_file=f"/tmp/{file_name}", path=f"{output_path}/{file_name}")


def main(args):
    download_file(args.file_uri, args.file_name, args.output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("-f", "--file-uri", dest="file_uri", type=str, help="File URI")
    parser.add_argument("-o", "--output-path", dest="output_path", type=str, help="Output path to store file")
    parser.add_argument("-n", "--file-name", dest="file_name", type=str, help="File name")

    args = parser.parse_args()
    main(args)

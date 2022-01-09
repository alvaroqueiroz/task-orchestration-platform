import boto3
import json
import argparse
import requests

from utils.logger import get_std_logger


logger = get_std_logger()


def download_file(file_uri, output_path):
    res = requests.get(file_uri)
    logger.info(f"Starting download file {args.file_uri} to {args.output_path}")
    logger.info(f"Writing file...")
    with open(output_path, 'wb') as f:
        f.write(res.content)


def main(args):
    download_file(args.file_uri, args.output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("-f", "--file-uri", dest="file_uri", type=str, help="File URI")
    parser.add_argument("-o", "--output-path", dest="output_path", type=str, help="Output path to store file")

    args = parser.parse_args()
    main(args)

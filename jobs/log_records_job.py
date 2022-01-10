import json
import argparse
import awswrangler as wr

from utils.logger import get_std_logger


logger = get_std_logger()


def fetch_s3_file(s3_file_path, compression_type="gzip"):
    try:
        logger.info(f"Reading csv.gz file from s3 path: {s3_file_path}")
        df = wr.s3.read_csv(path=s3_file_path, compression=compression_type)
        return df
    except Exception as err:
        logger.error(f"Cannot read csv from bucket: {compression_type} with error: {err}")
        return None


def log_records(json_string):
    try:
        records = json.loads(json_string)
        logger.info("Starting log records")
        for line in records:
            logger.info(line)
    except ValueError as err:
        logger.info(f"Error to parse json string. Error: {err}")
        return False

    logger.info("Logged all records")
    return True

def main(file_path, compression_type):
    df = fetch_s3_file(file_path, compression_type)
    json_file = df.to_json(orient="records")
    result = log_records(json_file)
    if result:
        logger.info("Job finished!")
        return True
    else:
        logger.error("Job finished with error!")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job to download csv file and upload to s3 bucket")
    parser.add_argument("-f", "--file-path", dest="file_path", type=str, help="S3 file URI")
    parser.add_argument("-c", "--compression", dest="compression_type", type=str, help="Compression type. default=gzip")

    args = parser.parse_args()
    main(args.file_path, args.compression_type)

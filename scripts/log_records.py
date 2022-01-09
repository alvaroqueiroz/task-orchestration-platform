import json
import argparse
import awswrangler as wr

from utils.logger import get_std_logger


logger = get_std_logger()


def read_file(file_path, compression_type="gzip"):
    return wr.s3.read_csv(path=file_path, compression=compression_type)


def print_records(json_file):
    records = json.loads(json_file)
    for line in records:
        logger.info(line)


def main(args):
    df = read_file(args.file_path, args.compression_type)
    json_file = df.to_json(orient="records")
    print_records(json_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("-f", "--file-path", dest="file_path", type=str, help="S3 file URI")
    parser.add_argument("-c", "--compression", dest="compression_type", type=str, help="Compression type. default=gzip")

    args = parser.parse_args()
    main(args)

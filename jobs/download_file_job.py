import argparse
import requests
import awswrangler as wr

from .utils.logger import get_std_logger


logger = get_std_logger()


def download_file(file_uri, file_name):
    try:
        logger.info(f"Starting download file {file_uri}")
        res = requests.get(file_uri)
        
        if res.status_code != 200:
            logger.error(f"Cannot download file with status_code={res.status_code}")
            return None
        
        logger.info(f"Writing temp file to /tmp/{file_name}")
        with open(f"/tmp/{file_name}", 'wb') as f:
            f.write(res.content)
        return f"/tmp/{file_name}"
    except Exception as e:
        logger.error(f"Cannot download file with exception {e}")
        return None
    

def upload_to_s3(local_file_path, s3_bucket_path):
    logger.info(f"Uploading file to s3 bucket: {s3_bucket_path}")
    try:
        wr.s3.upload(local_file=local_file_path, path=s3_bucket_path)
        logger.info("File was uploaded with success!")
        return True
    except Exception as e:
        logger.error(f"Cannot upload file to s3 bucket: {s3_bucket_path} with exception: {e}")
        return False

def main(file_uri, output_path, file_name):
    s3_output_path = f"{output_path}/{file_name}"
    local_file_path = download_file(file_uri, file_name)
    result = upload_to_s3(local_file_path, s3_output_path)
    if result:
        logger.info(f"Downloaded file {file_name} and uploaded to {output_path} with success!")
    else:
        logger.error("Job finished with error!")

    logger.info("Finished job.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("-f", "--file-uri", dest="file_uri", type=str, help="File URI")
    parser.add_argument("-o", "--output-path", dest="output_path", type=str, help="Output path to store file")
    parser.add_argument("-n", "--file-name", dest="file_name", type=str, help="File name")

    args = parser.parse_args()
    main(args.file_uri, args.output_path, args.file_name)

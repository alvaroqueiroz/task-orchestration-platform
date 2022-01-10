import mock
import argparse
import unittest

from unittest.mock import Mock, patch, mock_open

from jobs import download_file_job
from jobs.download_file_job import download_file, upload_to_s3

class TestDownloadFileJob(unittest.TestCase):
    
    @patch('requests.get')
    def test_download_file_with_return_correct(self, request_mock):
        # prepare
        file_uri = "http://test-url/file.csv.gz"
        file_name = "file.csv.gz"
        temp_local_file = f"/tmp/{file_name}"
        
        # mock
        request_mock.return_value.status_code = 200
        request_mock.return_value.content = bytes(b"Fake csv")

        # execute
        result = download_file(file_uri, file_name)
        
        # assert
        self.assertEqual(result, temp_local_file)
        request_mock.assert_called_once_with(file_uri)

    @patch('jobs.download_file_job.open', create=True)
    @patch('requests.get')
    def test_download_file_if_file_was_written(self, request_mock, open_mock):
        # prepare
        file_uri = "http://test-url/file.csv.gz"
        file_name = "file.csv.gz"
        temp_local_file = f"/tmp/{file_name}"
        request_mock_content = bytes(b"Fake csv")
        
        # mock
        request_mock.return_value.status_code = 200
        request_mock.return_value.content = request_mock_content
        
        # execute
        result = download_file(file_uri, file_name)
        
        open_mock.assert_called_with(temp_local_file, "wb")
        
    @patch('requests.get')
    def test_download_file_with_exception_status_code(self, request_mock):
        # prepare
        file_uri = "http://test-url/file.csv.gz"
        file_name = "file.csv.gz"
        
        # mock
        request_mock.return_value.status_code = 404
        request_mock.return_value.content = bytes(b"Fake csv")

        # execute
        result = download_file(file_uri, file_name)
        
        # assert
        self.assertEqual(result, None)
        request_mock.assert_called_once_with(file_uri)
    
    def test_download_file_with_wrong_file_uri(self):
         # prepare
        file_uri = "http://test-url/file.csv.gz"
        file_name = "file.csv.gz"

        # execute
        result = download_file(file_uri, file_name)
        
        # assert
        self.assertEqual(result, None)
        
    @patch('awswrangler.s3.upload')
    def test_upload_to_s3_with_success(self, mock_wrangler_s3_upload):
        # prepare
        local_file_path = "/tmp/file.csv.gz"
        s3_bucket_path = "s3://mock-bucket-test"
        
        # execute
        result = upload_to_s3(local_file_path, s3_bucket_path)
        
        # assert
        self.assertEqual(result, True)
        mock_wrangler_s3_upload.assert_called_once_with(local_file=local_file_path, path=s3_bucket_path)
        
    @patch('awswrangler.s3.upload')
    def test_upload_to_s3_with_error(self, mock_wrangler_s3_upload):
        # prepare
        local_file_path = "/tmp/file.csv.gz"
        s3_bucket_path = "s3://mock-bucket-test"
        
        # mock
        mock_wrangler_s3_upload.side_effect = Exception("TestException")
        
        # execute
        result = upload_to_s3(local_file_path, s3_bucket_path)
        
        # assert
        self.assertRaises(Exception, upload_to_s3)
        self.assertEqual(result, False)

    @patch('jobs.download_file_job.upload_to_s3')
    @patch('jobs.download_file_job.download_file')
    def test_main_method_with_success(self, download_file_mock, upload_to_s3_mock):
        # prepare 
        s3_output_path = "s3://mock-bucket-test"
        file_name = "file.csv.gz"
        file_uri = "http://file-uri.com/file.csv.gz"
        local_file_path = f"/tmp/{file_name}"

        download_file_mock.return_value = f"/tmp/{file_name}"
        upload_to_s3_mock.return_value = True

        # execute
        download_file_job.main(file_uri, s3_output_path, file_name)

        # assert
        download_file_mock.assert_called_once_with(file_uri, file_name)
        upload_to_s3_mock.assert_called_once_with(local_file_path, f"{s3_output_path}/{file_name}")

    @patch('jobs.download_file_job.upload_to_s3')
    @patch('jobs.download_file_job.download_file')
    def test_main_method_with_error(self, download_file_mock, upload_to_s3_mock):
        # prepare 
        s3_output_path = "s3://mock-bucket-test"
        file_name = "file.csv.gz"
        file_uri = "http://file-uri.com/file.csv.gz"
        local_file_path = f"/tmp/{file_name}"

        download_file_mock.return_value = f"/tmp/{file_name}"
        upload_to_s3_mock.return_value = False

        # execute
        download_file_job.main(file_uri, s3_output_path, file_name)

        # assert
        download_file_mock.assert_called_once_with(file_uri, file_name)
        upload_to_s3_mock.assert_called_once_with(local_file_path, f"{s3_output_path}/{file_name}")
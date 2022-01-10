import unittest
import pandas as pd

from unittest.mock import patch

from jobs.log_records_job import fetch_s3_file, log_records, main

class TestDownloadFileJob(unittest.TestCase):
    
    @patch('awswrangler.s3.read_csv')
    def test_fetch_s3_file_with_success(self, mock_wrangler_s3_read_csv):
        # prepare
        s3_file_path = "s3://mock-bucket-test/test.csv.gz"
        compression_type = "gzip"
        
        # execute
        result = fetch_s3_file(s3_file_path, compression_type)

        # mock
        mock_wrangler_s3_read_csv.return_value = "mock dataframe"
        
        # assert
        self.assertIsNotNone(result)
        mock_wrangler_s3_read_csv.assert_called_once_with(path=s3_file_path, compression=compression_type)

    @patch('awswrangler.s3.read_csv')
    def test_fetch_s3_file_with_error(self, mock_wrangler_s3_read_csv):
        # prepare
        s3_file_path = "s3://mock-bucket-test/test.csv.gz"
        compression_type = "gzip"
        
        # mock
        mock_wrangler_s3_read_csv.side_effect = Exception("TestException")

        # execute
        result = fetch_s3_file(s3_file_path, compression_type)
        
        # assert
        self.assertIsNone(result)
        self.assertRaises(Exception)
        mock_wrangler_s3_read_csv.assert_called_once_with(path=s3_file_path, compression=compression_type)

    def test_log_records_with_success(self):
        # prepare
        json_string = '[{"foo": "bar"}, {"foo2": "bar2"}, {"foo3": "bar3"}]'

        # execute
        result = log_records(json_string)

        # assert
        self.assertTrue(result)

    def test_log_records_with_error(self):
        # prepare
        bad_json_string = '[{"foo": "bar, {"foo2": "bar2"}, {"foo3": "bar3"}]'

        # execute
        result = log_records(bad_json_string)

        # assert
        self.assertFalse(result)
        self.assertRaises(ValueError)

    @patch('jobs.log_records_job.fetch_s3_file')
    def test_main_method_with_success(self, fetch_s3_file_mock):
         # prepare
        s3_file_path = "s3://mock-bucket-test/test.csv.gz"
        compression_type = "gzip"
        mock_record_json = [{"foo": "bar"}, {"foo2": "bar2"}, {"foo3": "bar3"}]

        fetch_s3_file_mock.return_value = pd.DataFrame(mock_record_json)

        # execute
        result = main(s3_file_path, compression_type)

        # assert
        self.assertTrue(result)
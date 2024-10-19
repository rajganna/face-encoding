import logging
import sys
import unittest
from unittest.mock import patch

from app.lib.logging_config import configure_logging


class TestLoggingConfiguration(unittest.TestCase):

    @patch('logging.basicConfig')
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_configure_logging(self, mock_stream_handler, mock_file_handler, mock_basic_config):
        configure_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                mock_stream_handler.return_value,
                mock_file_handler.return_value,
            ]
        )

        mock_stream_handler.assert_called_once_with(sys.stdout)
        mock_file_handler.assert_called_once_with('app.log')

import unittest
from unittest.mock import patch, MagicMock, call # Added call for checking calls in order
import sys
import os

# Adjust sys.path to include the parent directory (project root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app import db # Assuming app.py creates db = SQLAlchemy()
from models import URL
from sqlalchemy.exc import IntegrityError # Import IntegrityError

class TestURLModel(unittest.TestCase):

    def setUp(self):
        """Set up a test Flask app and app context."""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # No need for db.create_all() as we are mocking db interactions for these tests

    def tearDown(self):
        """Clean up app context."""
        if self.app_context:
            self.app_context.pop()

    @patch('app.db.session.rollback') # Mock rollback to prevent issues during error handling
    @patch('app.db.session.flush')    # Now patching flush
    def test_generate_short_url_standard_length(self, mock_flush, mock_rollback):
        """Test standard generation of a 6-character short URL."""
        # Configure flush to succeed on the first call (no side_effect means it returns None by default)
        mock_flush.return_value = None 

        url_instance = URL(destination_url="http://example.com")

        self.assertEqual(len(url_instance.short_url), 6)
        mock_flush.assert_called_once_with([url_instance]) # Check that flush was called with the instance
        mock_rollback.assert_not_called() # Rollback should not be called if successful

    @patch('app.db.session.rollback')
    @patch('app.db.session.flush')
    def test_generate_short_url_increases_length_to_7(self, mock_flush, mock_rollback):
        """Test that URL length increases to 7 after 10 collisions at length 6."""
        max_attempts_per_length = 10
        
        # Simulate 10 IntegrityErrors for length 6, then success for length 7
        # IntegrityError needs params: statement, parameters, orig
        side_effects = [IntegrityError("mock_statement", "mock_params", "mock_orig")] * max_attempts_per_length + [None]
        mock_flush.side_effect = side_effects

        url_instance = URL(destination_url="http://example.com/path2")
        
        self.assertEqual(len(url_instance.short_url), 7)
        # Total calls to flush should be max_attempts_per_length (for length 6) + 1 (for length 7)
        self.assertEqual(mock_flush.call_count, max_attempts_per_length + 1)
        self.assertEqual(mock_rollback.call_count, max_attempts_per_length) # Rollback for each IntegrityError

    @patch('app.db.session.rollback')
    @patch('app.db.session.flush')
    def test_generate_short_url_increases_length_to_8(self, mock_flush, mock_rollback):
        """Test that URL length increases to 8 after 10 collisions at length 6 and 10 at length 7."""
        max_attempts_per_length = 10
        
        # Simulate 10 IntegrityErrors for length 6
        errors_len_6 = [IntegrityError("mock_statement", "mock_params", "mock_orig")] * max_attempts_per_length
        # Simulate 10 IntegrityErrors for length 7
        errors_len_7 = [IntegrityError("mock_statement", "mock_params", "mock_orig")] * max_attempts_per_length
        # Success for length 8
        final_success = [None]
        
        mock_flush.side_effect = errors_len_6 + errors_len_7 + final_success

        url_instance = URL(destination_url="http://example.com/path3")
        
        self.assertEqual(len(url_instance.short_url), 8)
        # Total calls to flush should be 10 (len 6) + 10 (len 7) + 1 (len 8)
        self.assertEqual(mock_flush.call_count, (max_attempts_per_length * 2) + 1)
        self.assertEqual(mock_rollback.call_count, max_attempts_per_length * 2) # Rollback for each IntegrityError

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust sys.path to include the parent directory (project root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app import db # Assuming app.py creates db = SQLAlchemy()
from models import URL

class TestURLModel(unittest.TestCase):

    def setUp(self):
        """Set up a test Flask app and app context."""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        db.init_app(self.app)  # Initialize db with the app
        self.app_context = self.app.app_context()
        self.app_context.push()
        # If your models need to be created in the test database:
        # with self.app.app_context():
        #     db.create_all()

    def tearDown(self):
        """Clean up app context and database (if created)."""
        # with self.app.app_context():
        #     db.session.remove()
        #     db.drop_all()
        if self.app_context:
            self.app_context.pop()

    @patch('models.URL.query') # Patching the query attribute on the URL class
    def test_generate_short_url_standard_length(self, mock_query):
        """Test standard generation of a 6-character short URL."""
        # Configure the mock for URL.query.filter_by().first()
        mock_query.filter_by.return_value.first.return_value = None

        # Create a URL instance. __init__ will call generate_short_url.
        # We need a destination_url for the constructor.
        url_instance = URL(destination_url="http://example.com")

        self.assertEqual(len(url_instance.short_url), 6)
        # Verify that filter_by was called (at least once)
        mock_query.filter_by.assert_called()
        mock_query.filter_by().first.assert_called_once()

    @patch('models.URL.query')
    def test_generate_short_url_increases_length_to_7(self, mock_query):
        """Test that URL length increases to 7 after 10 collisions at length 6."""
        max_attempts_per_length = 10
        
        # Simulate 10 collisions for length 6, then success for length 7
        side_effects = [MagicMock(short_url="dummy")] * max_attempts_per_length + [None]
        mock_query.filter_by.return_value.first.side_effect = side_effects

        url_instance = URL(destination_url="http://example.com/path2")
        
        self.assertEqual(len(url_instance.short_url), 7)
        # Total calls to first() should be max_attempts_per_length (for length 6) + 1 (for length 7)
        self.assertEqual(mock_query.filter_by().first.call_count, max_attempts_per_length + 1)

    @patch('models.URL.query')
    def test_generate_short_url_increases_length_to_8(self, mock_query):
        """Test that URL length increases to 8 after 10 collisions at length 6 and 10 at length 7."""
        max_attempts_per_length = 10
        
        # Simulate 10 collisions for length 6
        effects_len_6 = [MagicMock(short_url="dummy6")] * max_attempts_per_length
        # Simulate 10 collisions for length 7
        effects_len_7 = [MagicMock(short_url="dummy7")] * max_attempts_per_length
        # Success for length 8
        final_effect = [None]
        
        mock_query.filter_by.return_value.first.side_effect = effects_len_6 + effects_len_7 + final_effect

        url_instance = URL(destination_url="http://example.com/path3")
        
        self.assertEqual(len(url_instance.short_url), 8)
        # Total calls to first() should be 10 (len 6) + 10 (len 7) + 1 (len 8)
        self.assertEqual(mock_query.filter_by().first.call_count, (max_attempts_per_length * 2) + 1)

if __name__ == '__main__':
    unittest.main()

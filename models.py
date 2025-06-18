from app import db
import string
import random
from sqlalchemy.exc import IntegrityError


class URL(db.Model):
    """
    Database URL model. Stores destination URL and short URL
    id: primary key
    destination_url: destination URL
    short_url: short URL
    enabled: flag to indicate if the URL is enabled
    """
    id = db.Column(db.Integer, primary_key=True)
    destination_url = db.Column(db.String(512), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)  # Add instance to session
        self._generate_and_set_short_url()  # Call the new method

    def _generate_and_set_short_url(self):
        length = 6
        max_attempts_per_length = 10
        characters = string.ascii_letters + string.digits

        while True:
            attempts_this_length = 0
            for _ in range(max_attempts_per_length):
                candidate_url = ''.join(random.choice(characters) for _ in range(length))
                self.short_url = candidate_url
                try:
                    # Attempt to flush this specific object to check for uniqueness
                    # The object is already in the session from __init__
                    db.session.flush([self]) 
                    return  # Success, unique URL found and flushed
                except IntegrityError:
                    db.session.rollback()  # Rollback due to unique constraint violation
                    attempts_this_length += 1
                    # Continue to next attempt in the inner loop
                except Exception as e:
                    db.session.rollback() # Rollback for any other error during flush
                    # For now, treat as a failed attempt and continue.
                    # A more robust implementation might log this error or re-raise if unexpected.
                    attempts_this_length += 1
            
            # If max_attempts_per_length reached for current length
            length += 1
            # The outer loop will restart with the new length

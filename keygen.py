import secrets
import string

from sqlalchemy.orm import Session
from . import crud

# Make random string for .url and .admin_url attributes
def create_random_key(length: int = 5) -> str:
    # Better than previous attempt where I hard-coded A-Z
    chars = string.ascii_uppercase + string.digits
    # Uses secrets module to randomly choose 5 chars
    return "".join(secrets.choice(chars) for _ in range(length))

def create_unique_random_key(db: Session) -> str:
    key = create_random_key()
    # Making a random key if key already exists in database
    while crud.get_db_url_by_key(db, key):
        key = create_random_key()
    return key
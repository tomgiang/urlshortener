"""
database.py has info about database connection. models.py describe content of my database

Code looks like the code from schemas.py

schemas.py => defined what data my API expected form client and server
models.py => declare how data should be stored in database
"""

from sqlalchemy import Boolean, Column, Integer, String

from .database import Base

# Defining a database model; URL is a subclass of Base
class URL(Base):
    __tablename__ = "urls"

    # Database's primary key
    id = Column(Integer, primary_key=True)
    # This will have a random string that'll be a part of the shortened URL
    key = Column(String, unique=True, index=True)
    # Can give secret key to user; has the ability to manage shortened URL and see stats
    secret_key = Column(String, unique=True, index=True)
    # Original, unshortened url
    # uniqueness has to be false, so different users can be sent to the same URL
    target_url = Column(String, index=True)
    # Helpful b/c instead of deleting the database entry when a user wants delete the shortened URL, make the entry inactive instead
    is_active = Column(Boolean, default=True)
    # Increases when someone clicks the shortened link
    clicks = Column(Integer, default=0)

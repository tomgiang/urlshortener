# Create, Read, Update, and Delete (CRUD)

from sqlalchemy.orm import Session

from . import keygen, models, schemas

def create_db_url(db: Session, url: schemas.URLBase) -> models.URL:
    # One Issue: The code below can return a key that already exists
    # key = keygen.create_random_key()
    # secret_key = keygen.create_random_key(length=8)
    key = keygen.create_unique_random_key(db)
    # secret_key doesn't need to be all unique b/c "key" is guaranteed to be unique. 
    # Thus, the whole thing is unique
    # Good b/c (1) it shows the associated key and (2) not hitting database again
    secret_key = f"{key}_{keygen.create_random_key(length=8)}"
    db_url = models.URL(
        target_url=url.target_url, key=key, secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

# Tells me if key already exists in database
# Returns either None or the database entry w/ provided key
def get_db_url_by_key(db: Session, url_key: str) -> models.URL:
    return (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )

# Checks database for active database entry w/ provided secret_key
# Returns similar to the function above
def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    return (
        db.query(models.URL)
        .filter(models.URL.secret_key == secret_key, models.URL.is_active)
        .first()
    )
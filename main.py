import validators
from fastapi import Depends, FastAPI, HTTPException, Request
# Returns HTTP redirect that forwards request of client
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from . import crud, models, schemas
from .database import SessionLocal, engine
from .config import get_settings

app = FastAPI()
#Binds database engine wtih something in models.py
models.Base.metadata.create_all(bind=engine)

# Create/yield new database sessions w/ each request
# try..finally close database connection in any case, even when during errors
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)

@app.get("/{url_key}")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(get_db)
    ):
    """
    Streamlined by crud.get_db_url_by_key
   
    # Look for an active URL entry in database
    db_url = (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )
    """
    # If the URL is in the database, then return
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        return RedirectResponse(db_url.target_url)
    else:
    # If not, return "URL not found"
        raise_not_found(request)

# Define new API endpoint at "/admin/{secret_key}" URL
@app.get(
    "/admin/{secret_key}",
    # Easy name to refer back to
    name="administration info",
    # Expect URLInfo schema
    response_model=schemas.URLInfo,
)
def get_url_info(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        db_url.url = db_url.key
        db_url.admin_url = db_url.secret_key
        return db_url
    else:
        raise_not_found(request)

def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url

# Path Opertation Decorator??
# Ensures that function below responds to any POST requests at /url path
@app.post("/url", response_model=schemas.URLInfo)

# Requires URLBase schema as an argument and depends on database session
# Passing get_db into Depends() => make a database session for request and close session when request is finished
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    # Ensures target_url is valid
    # If not valid, call raise_bad_request
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")

    """
    Streamlined by using crud.create_db_url()

    # Makes random strings
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = "".join(secrets.choice(chars) for _ in range(5))
    secret_key = "".join(secrets.choice(chars) for _ in range(8))

    # Creates database entry for target_url
    db_url = models.URL(
        target_url=url.target_url, key=key, secret_key=secret_key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    """
    # Add key & secret_key to db_url to match required URLInfo schema
    db_url = crud.create_db_url(db=db, url=url)
    db_url.url = db_url.key
    db_url.admin_url = db_url.secret_key

    return db_url


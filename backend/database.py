from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base() 

def get_db():
    """Gives a database session to an endpoint and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close() 


        
from sqlalchemy.orm import Session
from backend import models

# users
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = models.User(username = username, email = email, hashed_password = hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 

# Logs 
def save_log(db: Session, user_id: int, endpoint: str, input_text: str, output_text: str):
    log = models.Log(
        user_id = user_id, endpoint = endpoint, 
        input_text = input_text, output_text = output_text,
    ) 
    db.add(log)
    db.commit()
    db.refresh(log)
    return log 

def logs(db: Session, user_id: int, limit: int = 50):
    return (
        db.query(models.Log).filter(models.Log.user_id == user_id).order_by(models.Log.id.desc()).limit(limit).all() 
    )

# ---------- Logs ----------
def get_logs(db: Session, user_id: int, limit: int = 50):
    return (
        db.query(models.Log)
        .filter(models.Log.user_id == user_id)
        .order_by(models.Log.id.desc())      # newest first
        .limit(limit)
        .all()
    )


def get_log(db: Session, log_id: int):
    return db.query(models.Log).filter(models.Log.id == log_id).first()


# ---------- Feedback ----------
def create_feedback(db: Session, user_id: int, rating: int, comment, log_id):
    fb = models.Feedback(user_id=user_id, rating=rating, comment=comment, log_id=log_id)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


def get_feedback(db: Session, user_id: int):
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.user_id == user_id)
        .order_by(models.Feedback.id.desc())
        .all()
    )
from sqlalchemy.orm import Session

import models
import schemas

# ======= Create user

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# ======= get user by id

def get_user_by_id(db: Session, user_id: int):
    return (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

# create note

def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(
        title=note.title,
        content=note.content,
        tags=note.tags,
        user_id=note.user_id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note

# ========== get all notes

def get_all_notes(db: Session):
    return (
        db.query(models.Note)
        .order_by(models.Note.created_at.desc())
        .all()
    )

# ======== get note by id

def get_note_by_id(db: Session, note_id: int):
    return (
        db.query(models.Note)
        .filter(models.Note.id == note_id)
        .first()
    )

# ======== update note

def update_note(db: Session, note_id: int, note: schemas.NoteUpdate):
    db_note = get_note_by_id(db, note_id)

    if not db_note:
        return None

    update_data = note.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_note, key, value)

    db.commit()
    db.refresh(db_note)

    return db_note

# ========= delete note

def delete_note(db: Session, note_id: int):
    db_note = get_note_by_id(db, note_id)

    if not db_note:
        return None

    db.delete(db_note)
    db.commit()

    return db_note
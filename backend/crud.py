from sqlalchemy.orm import Session

import models
import schemas
from ai_tags import generate_tags

# bulk import
from fastapi import UploadFile

# for normal search
from sqlalchemy import or_

# report
from collections import Counter


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

def get_all_users(db: Session):
    return db.query(models.User).order_by(models.User.name).all()

# create note

def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(
        title=note.title,
        content=note.content,
        tags=generate_tags(note.content),
        user_id=note.user_id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # Load the related user
    db.refresh(db_note, attribute_names=["user"])

    # Add user_name for the response
    db_note.user_name = db_note.user.name

    return db_note

# ========== Get notes with pagination

def get_all_notes(db: Session, skip: int = 0, limit: int = 3):

    notes = (
        db.query(models.Note)
        .order_by(models.Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for note in notes:
        note.user_name = note.user.name

    return notes

# ========== Total notes count

def get_notes_count(db: Session):

    return db.query(models.Note).count()

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

    if "content" in update_data:
        db_note.tags = generate_tags(db_note.content)

    db.commit()
    db.refresh(db_note)

    db.refresh(db_note, attribute_names=["user"])
    db_note.user_name = db_note.user.name

    return db_note


# ========= delete note

def delete_note(db: Session, note_id: int):

    db_note = get_note_by_id(db, note_id)

    if not db_note:
        return None

    # Load related user
    db.refresh(db_note, attribute_names=["user"])

    # Add user_name before deleting
    db_note.user_name = db_note.user.name

    db.delete(db_note)
    db.commit()

    return db_note

# bulk import 

def import_notes(db: Session, file: UploadFile):

    content = file.file.read().decode("utf-8")

    notes = content.split("---")

    notes = [note.strip() for note in notes if note.strip()]

    imported_count = 0

    for note in notes:

        lines = note.splitlines()

        note_data = {}

        for line in lines:

            if line.startswith("Title:"):
                note_data["title"] = line.replace("Title:", "").strip()

            elif line.startswith("Content:"):
                note_data["content"] = line.replace("Content:", "").strip()

            elif line.startswith("User:"):
                note_data["user_id"] = int(line.replace("User:", "").strip())

        # ==========================
        # Check if the user exists
        # ==========================
        user = db.query(models.User).filter(
            models.User.id == note_data["user_id"]
        ).first()

        if not user:
            continue

        # ==========================
        # Create Note
        # ==========================
        db_note = models.Note(
            title=note_data["title"],
            content=note_data["content"],
            tags=generate_tags(note_data["content"]),
            user_id=note_data["user_id"]
        )

        db.add(db_note)

        imported_count += 1

    db.commit()

    return {
        "message": f"{imported_count} notes imported successfully"
    }

# normal search

def search_notes(db: Session, keyword: str):

    notes = (
        db.query(models.Note)
        .filter(
            or_(
                models.Note.title.ilike(f"%{keyword}%"),
                models.Note.content.ilike(f"%{keyword}%"),
                models.Note.tags.ilike(f"%{keyword}%")
            )
        )
        .order_by(models.Note.created_at.desc())
        .all()
    )

    for note in notes:
        note.user_name = note.user.name

    return notes

# reports 

def get_reports(db: Session):

    total_notes = db.query(models.Note).count()

    total_users = db.query(models.User).count()

    all_notes = db.query(models.Note).all()

    tags = []

    for note in all_notes:

        if note.tags:

            tags.extend(
                [tag.strip() for tag in note.tags.split(",")]
            )

    if tags:

        tag_counter = Counter(tags)

        most_used_tag = tag_counter.most_common(1)[0][0]

    else:

        most_used_tag = "N/A"

    return {

        "total_notes": total_notes,

        "total_users": total_users,

        "most_used_tag": most_used_tag,

        "imported_notes": total_notes

    }
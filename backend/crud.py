from sqlalchemy.orm import Session

import models
import schemas
from ai_tags import generate_tags

# bulk import
from fastapi import HTTPException, UploadFile
from tag_generator import generate_tags

# for normal search
from sqlalchemy import or_

# report
from collections import Counter
# tag summery
from sqlalchemy import text


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
        user_id=note.user_id,
        is_imported=False
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

def get_all_notes(db: Session,skip: int = 0,limit: int = 3,tag: str | None = None):

    query = db.query(models.Note)

    # Optional tag filter
    if tag:

        query = query.filter(
            models.Note.tags.ilike(f"%{tag}%")
        )

    notes = (
        query
        .order_by(models.Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for note in notes:
        note.user_name = note.user.name

    return notes

# ========== Total notes count

def get_notes_count(db: Session,tag: str | None = None):

    query = db.query(models.Note)

    if tag:

        query = query.filter(
            models.Note.tags.ilike(f"%{tag}%")
        )

    return query.count()

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

# ==========================
# Bulk Import Notes
# ==========================
def import_notes(
    db: Session,
    owner_id: int,
    file: UploadFile
):

    # ==========================
    # Check Owner Exists
    # ==========================
    user = (
        db.query(models.User)
        .filter(models.User.id == owner_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # ==========================
    # Read File
    # ==========================
    content = file.file.read().decode("utf-8")

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    imported_count = 0

    # ==========================
    # Create Notes
    # ==========================
    for line in lines:

        title = (
            line[:50] + "..."
            if len(line) > 50
            else line
        )
        db_note = models.Note(

            title=title,

            content=line,

            tags=generate_tags(line),

            user_id=owner_id,

            is_imported=True

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

    # Total Notes
    total_notes = db.query(models.Note).count()

    # Total Users
    total_users = db.query(models.User).count()

    # Imported Notes
    imported_notes = db.query(models.Note).filter(
        models.Note.is_imported == True
    ).count()

    # Most Used Tag
    all_notes = db.query(models.Note).all()

    tags = []

    for note in all_notes:

        if note.tags:

            tags.extend(
                [tag.strip() for tag in note.tags.split(",") if tag.strip()]
            )

    if tags:

        tag_counter = Counter(tags)

        most_used_tag = tag_counter.most_common(1)[0][0]

    else:

        most_used_tag = "No Tags"

    return {

        "total_notes": total_notes,

        "total_users": total_users,

        "most_used_tag": most_used_tag,

        "imported_notes": imported_notes

    }

# tag summery
def get_tag_summary(db: Session):

    query = text("""
        SELECT
            tags,
            COUNT(*) AS note_count
        FROM notes
        WHERE tags IS NOT NULL
        GROUP BY tags
        HAVING COUNT(*) > 1
        ORDER BY note_count DESC
    """)

    result = db.execute(query)

    return [
        {
            "tag": row.tags,
            "count": row.note_count
        }
        for row in result
    ]

# long notes
def get_long_notes(db: Session):

    result = db.execute(
        text("""
            SELECT
                id,
                title,
                content,
                tags
            FROM notes
            WHERE LEN(content) >
            (
                SELECT AVG(LEN(content))
                FROM notes
            )
            ORDER BY LEN(content) DESC
        """)
    )

    return [
        {
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "tag": row.tags
        }
        for row in result
    ]

# user notes
def get_user_notes_report(db: Session):

    result = db.execute(
        text("""
            SELECT
                u.id,
                u.name,
                u.email,
                COUNT(n.id) AS total_notes
            FROM users u
            LEFT JOIN notes n
                ON u.id = n.user_id
            GROUP BY
                u.id,
                u.name,
                u.email
            ORDER BY
                total_notes DESC,
                u.name
        """)
    )

    return [
        {
            "user_id": row.id,
            "name": row.name,
            "email": row.email,
            "total_notes": row.total_notes
        }
        for row in result
    ]
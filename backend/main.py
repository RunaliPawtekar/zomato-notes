from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, engine, get_db
from fastapi import UploadFile, File
from auth import verify_token
import time
from fastapi import BackgroundTasks
from background_tasks import simulate_note_indexing
from algorithms import (
    insertion_sort_by_key,
    binary_search_iterative,
    binary_search_recursive,
    linear_search
)

import json
import logging

from ai_service import get_ai_response
from prompts import AUTO_TAG_PROMPT

from embedding_service import (
    get_embedding,
    cosine_similarity,
    cache_note_embedding,
    remove_note_embedding
)

# Create FastAPI app
app = FastAPI(
    title="Zomato Notes API",
    version="1.0.0"
)

# ==========================
# Process Time Middleware
# ==========================
@app.middleware("http")
async def add_process_time_header(request, call_next):

    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{process_time:.4f} sec"

    return response


# ==========================
# CORS Middleware
# ==========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Welcome to Zomato Notes API"
    }


@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

@app.post("/notes", response_model=schemas.NoteResponse)
def create_note(
    note: schemas.NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    created_note = crud.create_note(
        db=db,
        note=note
    )
    cache_note_embedding(
        created_note.title,
        created_note.content
    )

    background_tasks.add_task(
        simulate_note_indexing,
        created_note.id
    )

    ai_suggestion = None

    try:

        ai_response = get_ai_response(

            user_message=created_note.content,

            system_prompt=AUTO_TAG_PROMPT

        )

        ai_suggestion = json.loads(
            ai_response
        )

    except Exception:

        logging.exception(
            "AI suggestion failed"
        )

    return {

        "id": created_note.id,
        "title": created_note.title,
        "content": created_note.content,
        "tags": created_note.tags,
        "created_at": created_note.created_at,
        "updated_at": created_note.updated_at,
        "user_id": created_note.user_id,
        "user_name": created_note.user.name,
        "ai_suggestion": ai_suggestion

    }

@app.get("/notes/search")
def search_notes(
    keyword: str | None = None,
    sort_by: str = "created_at",
    skip: int = 0,
    limit: int = 3,
    db: Session = Depends(get_db)
):
    # Get ALL notes from database
    notes = crud.get_all_notes(
        db=db,
        skip=0,
        limit=1000
    )

    # Convert database notes to dictionaries
    items = []

    for note in notes:
        items.append({
            "title": note.title,
            "content": note.content,
            "tags": note.tags,
            "id": note.id,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "user_id": note.user_id,
            "user_name": note.user_name
        })

    # -----------------------------
    # SEARCH
    # -----------------------------

    # -----------------------------
    # SEARCH
    # -----------------------------

    if keyword:

        keyword = keyword.lower().strip()

        filtered_items = []

        for item in items:

            title = (item["title"] or "").lower()
            content = (item["content"] or "").lower()
            tags = (item["tags"] or "").lower()

            score = 0

            # Search in title
            score += title.count(keyword) * 3

            # Search in tags
            score += tags.count(keyword) * 2

            # Search in content
            score += content.count(keyword)

            if score > 0:

                item["score"] = score

                filtered_items.append(item)

        items = insertion_sort_by_key(
            filtered_items,
            "score"
        )

    # -----------------------------
    # SORT
    # -----------------------------

    if not keyword:

        allowed_keys = [
            "title",
            "content",
            "tags",
            "id",
            "created_at",
            "updated_at"
        ]

        if sort_by not in allowed_keys:
            sort_by = "created_at"

        items = insertion_sort_by_key(
            items,
            sort_by
        )

    # -----------------------------
    # TOTAL
    # -----------------------------

    total = len(items)

    # -----------------------------
    # PAGINATION
    # -----------------------------

    paginated_items = items[
        skip:skip + limit
    ]

    # -----------------------------
    # RESPONSE
    # -----------------------------

    return {
        "total": total,
        "notes": paginated_items
    }


# smart search 
@app.get("/notes/smart-search")
def smart_search(
    q: str,
    db: Session = Depends(get_db)
):

    query_embedding = get_embedding(q)

    notes = crud.get_all_notes_for_search(db)

    ranked_notes = []

    for note in notes:

        text = f"{note.title} {note.content}"

        note_embedding = get_embedding(text)

        score = cosine_similarity(
            query_embedding,
            note_embedding
        )

        ranked_notes.append(
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "tags": note.tags,
                "score": round(score, 4),
                "user_name": note.user.name if note.user else ""
            }
        )

    ranked_notes.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked_notes[:3]

@app.get("/notes")
def get_notes(
    skip: int = 0,
    limit: int = 3,
    tag: str | None = None,
    db: Session = Depends(get_db)
):

    notes = crud.get_all_notes(
        db=db,
        skip=skip,
        limit=limit,
        tag=tag
    )

    total = crud.get_notes_count(db=db,tag=tag)

    return {
        "total": total,
        "notes": notes
    }

@app.get("/notes/lookup")
def lookup_note(
    title: str,
    algo: str = "iterative",
    db: Session = Depends(get_db)
):

    # Get notes sorted alphabetically
    notes = crud.get_notes_sorted_by_title(db)

    # Create normalized title list
    titles = [
        note.title.strip().lower()
        for note in notes
    ]

    # Normalize input title
    target = title.strip().lower()

    # Select algorithm
    if algo == "recursive":

        index = binary_search_recursive(
            titles,
            target,
            0,
            len(titles) - 1
        )

    else:

        index = binary_search_iterative(
            titles,
            target
        )

    # Not found
    if index == -1:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    # Return original note
    note = notes[index]

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "tags": note.tags,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "user_id": note.user_id,
        "user_name": note.user_name
    }

@app.get("/notes/quick-find")
def quick_find_note(
    tag: str,
    db: Session = Depends(get_db)
):

    notes = crud.get_all_notes_for_search(db)

    items = []

    for note in notes:

        items.append({

            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tags": note.tags,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
            "user_id": note.user_id,
            "user_name": note.user_name

        })

    result = linear_search(
        items,
        "tags",
        tag
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return result


@app.get("/notes/{note_id}", response_model=schemas.NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note_by_id(db, note_id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note

@app.put("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: int,
    note: schemas.NoteUpdate,
    db: Session = Depends(get_db)
):

    # Get existing note before updating
    existing_note = crud.get_note_by_id(db, note_id)

    if not existing_note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    # Store old values
    old_title = existing_note.title
    old_content = existing_note.content

    # Update note
    updated_note = crud.update_note(
        db,
        note_id,
        note
    )

    # Remove old embedding
    remove_note_embedding(
        old_title,
        old_content
    )

    # Cache new embedding
    cache_note_embedding(
        updated_note.title,
        updated_note.content
    )

    return updated_note

@app.delete("/notes/{note_id}", response_model=schemas.NoteResponse)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(verify_token)
):

    deleted_note = crud.delete_note(db, note_id)

    if not deleted_note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return deleted_note
# for bulk import 

@app.post("/notes/import")
def import_notes(
    owner_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return crud.import_notes(
        db=db,
        owner_id=owner_id,
        file=file
    )

# for reports

@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)

# for tag summery
@app.get("/reports/tag-summary")
def tag_summary(db: Session = Depends(get_db)):
    return crud.get_tag_summary(db)

# long notes
@app.get("/reports/long-notes")
def long_notes(db: Session = Depends(get_db)):
    return crud.get_long_notes(db)

# user notes
@app.get("/reports/user-notes")
def user_notes_report(db: Session = Depends(get_db)):
    return crud.get_user_notes_report(db)

# report/tags
@app.get("/reports/tags")
def get_tag_report(
    db: Session = Depends(get_db)
):
    return crud.get_tag_report(db)


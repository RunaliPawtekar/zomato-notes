from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, engine, get_db
from fastapi import UploadFile, File

# Create FastAPI app
app = FastAPI(
    title="Zomato Notes API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
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
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db=db, note=note)

@app.get("/notes/search", response_model=list[schemas.NoteResponse])
def search_notes(
    keyword: str,
    db: Session = Depends(get_db)
):
    return crud.search_notes(db, keyword)

@app.get("/notes")
def get_notes(
    skip: int = 0,
    limit: int = 3,
    db: Session = Depends(get_db)
):

    notes = crud.get_all_notes(
        db=db,
        skip=skip,
        limit=limit
    )

    total = crud.get_notes_count(db)

    return {
        "total": total,
        "notes": notes
    }


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
    updated_note = crud.update_note(db, note_id, note)

    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")

    return updated_note

@app.delete("/notes/{note_id}", response_model=schemas.NoteResponse)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    deleted_note = crud.delete_note(db, note_id)

    if not deleted_note:
        raise HTTPException(status_code=404, detail="Note not found")

    return deleted_note

# for bulk import 

@app.post("/notes/import")
def import_notes(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return crud.import_notes(db, file)

# for reports

@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException

# Create FastAPI app
app = FastAPI(
    title="Zomato Notes API",
    version="1.0.0"
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

@app.post("/notes", response_model=schemas.NoteResponse)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db=db, note=note)

@app.get("/notes", response_model=list[schemas.NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    return crud.get_all_notes(db)

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
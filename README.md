# Zomato Notes

## Project Overview

Zomato Notes is a full-stack incident knowledge management application
built for support engineers. It allows users to create, manage, search,
rank and intelligently analyze operational notes.

------------------------------------------------------------------------

# Tech Stack

-   Backend: FastAPI, SQLAlchemy ORM
-   Database: SQL Server (ZomatoNotesDB)
-   Frontend: HTML, CSS, JavaScript
-   AI Mock Service
-   sentence-transformers==3.0.0
-   Model: sentence-transformers/all-MiniLM-L6-v2

------------------------------------------------------------------------

# Repository Structure

``` text
backend/
frontend/
requirements.txt
.env.example
README.md
```

------------------------------------------------------------------------

# Environment Setup

## 1. Clone

``` bash
git clone <YOUR_PUBLIC_REPOSITORY_URL>
cd zomato-notes
```

## 2. Create Virtual Environment

``` bash
python -m venv venv
```

Activate

Windows

``` bash
venv\Scripts\activate
```

## 3. Install Dependencies

``` bash
pip install -r requirements.txt
```

## 4. Configure Environment

Create `.env`

``` env
DATABASE_URL=
MOCK_AI=1
GROQ_API_KEY=
```

Never commit the real `.env`.

Use `.env.example` in the repository.

------------------------------------------------------------------------

# Database

Create SQL Server database

    ZomatoNotesDB

Run the application.

Tables are created automatically.

No sample seed data is required. Smart Search uses the live notes stored
in ZomatoNotesDB.

------------------------------------------------------------------------

# Running Backend

``` bash
uvicorn main:app --reload
```

Swagger

    http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# Running Frontend

Open

    frontend/index.html

in the browser.

------------------------------------------------------------------------

# Part 1 Features

-   User CRUD
-   Note CRUD
-   Pagination
-   Reports
-   Import TXT
-   Background Task
-   Responsive Dashboard

## Example Create Note

Request

``` json
{
"title":"Delivery Delay",
"content":"Customer order delayed by 20 minutes.",
"user_id":3
}
```

Response

``` json
{
"id":21,
"title":"Delivery Delay",
"user_name":"Rohan",
"tags":"delivery",
"ai_suggestion":{
"tags":["delivery","delay"],
"summary":"Customer order delayed by 20 minutes."
}
}
```

------------------------------------------------------------------------

# Part 2 Ranking Engine

Implemented manually.

Features

-   Keyword Search
-   Occurrence Count Ranking
-   Binary Search
-   Sort by Date
-   Sort by Relevance
-   Quick Tags

Normal Search ranks by literal keyword occurrence.

------------------------------------------------------------------------

# Part 3 Intelligence Layer

## AI Auto Tagging

Implemented in `ai_service.py`

Uses

``` python
get_ai_response(user_message, system_prompt)
```

Default evaluation mode

    MOCK_AI=1

No API key required.

## Prompt Template

The prompt follows five sections.

1.  Instructions
2.  Context
3.  Input
4.  Constraints
5.  Output Format

Expected output

``` json
{
"tags":["delivery","delay"],
"summary":"Customer experienced delivery delay."
}
```

The backend parses the response using `json.loads()`.

If parsing fails:

-   exception is caught
-   raw response is logged
-   note is still created
-   `ai_suggestion` becomes `null`

## Apply Tag

When the user clicks **Apply Tag**

-   first suggested tag is applied
-   existing PUT endpoint updates the note

------------------------------------------------------------------------

# Smart Search

Endpoint

    GET /notes/smart-search?q=delivery delay

Uses

-   sentence-transformers==3.0.0
-   all-MiniLM-L6-v2
-   cosine similarity

Returns top 3 notes.

Example

``` json
[
{
"title":"Delivery Delay",
"score":0.9412
}
]
```

------------------------------------------------------------------------

# Normal Search vs Smart Search

  Normal Search      Smart Search
  ------------------ -------------------
  Keyword Match      Meaning Match
  Occurrence Count   Embeddings
  Manual Ranking     Cosine Similarity

------------------------------------------------------------------------

# One-time Model Download

The first execution downloads

    sentence-transformers/all-MiniLM-L6-v2

Internet is required only once.

Cached location (default)

    ~/.cache/huggingface

After caching:

-   No internet
-   No API key
-   Fully offline

------------------------------------------------------------------------

# Git Workflow

Branches

-   main
-   feature/part1-backend-frontend
-   feature/part2-ranking-engine
-   feature/part3-intelligence-layer

Each feature branch was merged into main.

Commits were made incrementally with meaningful commit messages.

------------------------------------------------------------------------

# API Summary

-   GET /notes
-   POST /notes
-   PUT /notes/{id}
-   DELETE /notes/{id}
-   GET /notes/search
-   GET /notes/smart-search
-   GET /reports

------------------------------------------------------------------------

# Future Improvements

-   Persistent vector storage
-   Better semantic ranking
-   Multiple AI providers

------------------------------------------------------------------------

# Author

Runali Pawtekar

-----------------------------------------------------------------------
# Zomato Notes

## API Examples

### 1. Get All Notes

**Request**

``` http
GET /notes?skip=0&limit=3
```

**Response**

``` json
{
  "total": 12,
  "notes": [
    {
      "id": 1,
      "title": "Delivery Delay",
      "content": "Customer order delayed by 20 minutes.",
      "tags": "delivery",
      "user_name": "Rohan Deshmukh"
    }
  ]
}
```

### 2. Get Single Note

``` http
GET /notes/1
```

``` json
{
  "id": 1,
  "title": "Delivery Delay",
  "content": "Customer order delayed by 20 minutes.",
  "tags": "delivery",
  "user_name": "Rohan Deshmukh"
}
```

### 3. Create Note

``` http
POST /notes
Content-Type: application/json
```

``` json
{
  "title":"Delivery Delay",
  "content":"Customer order delayed by 20 minutes.",
  "user_id":3
}
```

``` json
{
  "id":13,
  "title":"Delivery Delay",
  "tags":"delivery",
  "user_name":"Rohan Deshmukh",
  "ai_suggestion":{
    "tags":["delivery","delay","minutes"],
    "summary":"Customer order delayed by 20 minutes."
  }
}
```

### 4. Update Note

``` http
PUT /notes/13
```

``` json
{
  "title":"Delivery Delay Updated",
  "content":"Customer order delayed by 30 minutes.",
  "tags":"delay"
}
```

``` json
{
  "message":"Note updated successfully"
}
```

### 5. Delete Note

``` http
DELETE /notes/13
```

``` json
{
  "message":"Note deleted successfully"
}
```

### 6. Normal Search

``` http
GET /notes/search?q=delivery
```

``` json
[
  {
    "title":"Delivery Delay",
    "score":4
  }
]
```

### 7. Smart Search

``` http
GET /notes/smart-search?q=late food delivery
```

``` json
[
  {
    "title":"Delivery Delay",
    "score":0.9412
  },
  {
    "title":"Restaurant Issue",
    "score":0.9034
  },
  {
    "title":"Customer Complaint",
    "score":0.8871
  }
]
```

### 8. Reports

``` http
GET /reports
```

``` json
{
  "total_notes":12,
  "imported_notes":2,
  "manual_notes":10,
  "total_users":5
}
```

### 9. Import Notes

``` http
POST /notes/import
```

Response

``` json
{
  "message":"Notes imported successfully",
  "count":5
}
```

### 10. AI Apply Tag

After clicking **Apply Tag**, the frontend calls:

``` http
PUT /notes/13
```

``` json
{
  "tags":"delay"
}
```

Response

``` json
{
  "message":"Tag updated successfully"
}
```

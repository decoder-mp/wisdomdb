"""
Lore - Preserve and discover wisdom hidden in human experience.
"""

from typing import List
import random
import sqlite3
from datetime import datetime
from datetime import date
from routers import users, auth, comments, likes, bookmarks, ai


from fastapi import FastAPI
from pydantic import BaseModel

from routers import lore

app = FastAPI(title="Lore")

app.include_router(lore.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(bookmarks.router)
app.include_router(ai.router)

DB_NAME = "lore.db"

class LoreEntry(BaseModel):
    """Represents a single piece of human wisdom."""

    person: str
    profession: str
    years_experience: int
    theme: str
    question: str
    lore: str
    tags: List[str]


def get_connection():
    """Create and return a database connection."""

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create database tables if they do not exist."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS lore (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person TEXT NOT NULL,
        profession TEXT NOT NULL,
        years_experience INTEGER NOT NULL,
        theme TEXT NOT NULL,
        question TEXT NOT NULL,
        lore TEXT NOT NULL,
        tags TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


initialize_database()


@app.get("/")
def home():
    """Lore homepage."""

    return {
        "message": "Welcome to Lore",
        "mission": "Preserve human experience",
        "version": "0.9",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/lore")
def create_lore(entry: LoreEntry):
    """Store a new lore entry."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute(
        """
        INSERT INTO lore (
            person,
            profession,
            years_experience,
            theme,
            question,
            lore,
            tags,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry.person,
            entry.profession,
            entry.years_experience,
            entry.theme,
            entry.question,
            entry.lore,
            ",".join(entry.tags),
            datetime.utcnow().isoformat(),
        ),
    )

    conn.commit()
    conn.close()

    return {
        "status": "saved",
        "person": entry.person,
    }


@app.get("/lore")
def list_lore():
    """Return all lore entries."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute("""
        SELECT *
        FROM lore
    """)

    rows = db_cursor.fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "person": row["person"],
            "profession": row["profession"],
            "years_experience": row["years_experience"],
            "theme": row["theme"],
            "question": row["question"],
            "lore": row["lore"],
            "tags": row["tags"].split(","),
        }
        for row in rows
    ]


@app.get("/search")
def search_lore(topic: str):
    """
    Search lore entries by keyword.

    Example:
    /search?topic=leadership
    """

    conn = get_connection()
    db_cursor = conn.cursor()

    search_term = f"%{topic}%"

    db_cursor.execute(
        """
        SELECT *
        FROM lore
        WHERE
            lore LIKE ?
            OR question LIKE ?
            OR tags LIKE ?
            OR profession LIKE ?
            OR theme LIKE ?
        """,
        (
            search_term,
            search_term,
            search_term,
            search_term,
            search_term,
        ),
    )

    rows = db_cursor.fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "person": row["person"],
            "profession": row["profession"],
            "years_experience": row["years_experience"],
            "theme": row["theme"],
            "question": row["question"],
            "lore": row["lore"],
            "tags": row["tags"].split(","),
        }
        for row in rows
    ]


@app.get("/random")
def random_lore():
    """Return a random wisdom entry."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute("""
        SELECT *
        FROM lore
    """)

    rows = db_cursor.fetchall()

    conn.close()

    if not rows:
        return {
            "message": "Lore has not collected any wisdom yet."
        }

    row = random.choice(rows)

    return {
        "id": row["id"],
        "person": row["person"],
        "profession": row["profession"],
        "years_experience": row["years_experience"],
        "theme": row["theme"],
        "question": row["question"],
        "lore": row["lore"],
        "tags": row["tags"].split(","),
    }


@app.get("/themes/{theme_name}")
def get_theme(theme_name: str):
    """Return wisdom entries for a specific theme."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute(
        """
        SELECT *
        FROM lore
        WHERE LOWER(theme) LIKE LOWER(?)
        """,
        (f"%{theme_name}%",),
    )

    rows = db_cursor.fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "person": row["person"],
            "profession": row["profession"],
            "years_experience": row["years_experience"],
            "theme": row["theme"],
            "question": row["question"],
            "lore": row["lore"],
            "tags": row["tags"].split(","),
        }
        for row in rows
    ]


@app.get("/themes")
def list_themes():
    """Return all themes and their occurrence counts."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute("""
        SELECT theme, COUNT(*) AS count
        FROM lore
        GROUP BY theme
        ORDER BY count DESC
    """)

    rows = db_cursor.fetchall()

    conn.close()

    return [
        {
            "theme": row["theme"],
            "count": row["count"],
        }
        for row in rows
    ]


@app.get("/quote")
def quote():
    """Return a random wisdom quote."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute("""
        SELECT
            person,
            profession,
            years_experience,
            theme,
            question,
            lore
        FROM lore
    """)

    rows = db_cursor.fetchall()

    conn.close()

    if not rows:
        return {
            "message": "Lore has not collected any wisdom yet."
        }

    row = random.choice(rows)

    return {
        "quote": row["lore"],
        "person": row["person"],
        "profession": row["profession"],
        "years_experience": row["years_experience"],
        "theme": row["theme"],
        "question": row["question"],
        "attribution": (
            f"{row['person']}, "
            f"{row['profession']} "
            f"({row['years_experience']} years)"
        ),
    }
@app.get("/stats")
def stats():
    """Return statistics about the Lore archive."""

    conn = get_connection()
    db_cursor = conn.cursor()

    # Total entries
    db_cursor.execute("""
        SELECT COUNT(*)
        FROM lore
    """)
    total_entries = db_cursor.fetchone()[0]

    # Total unique themes
    db_cursor.execute("""
        SELECT COUNT(DISTINCT theme)
        FROM lore
    """)
    total_themes = db_cursor.fetchone()[0]

    # Most common theme
    db_cursor.execute("""
        SELECT theme, COUNT(*) AS count
        FROM lore
        GROUP BY theme
        ORDER BY count DESC
        LIMIT 1
    """)

    result = db_cursor.fetchone()

    conn.close()

    most_common_theme = None

    if result:
        most_common_theme = result["theme"]

    return {
        "total_entries": total_entries,
        "total_themes": total_themes,
        "most_common_theme": most_common_theme
    }
@app.get("/profession/{profession_name}")
def get_profession(profession_name: str):
    """Return wisdom entries from a profession."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute(
        """
        SELECT *
        FROM lore
        WHERE LOWER(profession) LIKE LOWER(?)
        """,
        (f"%{profession_name}%",)
    )

    rows = db_cursor.fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "person": row["person"],
            "profession": row["profession"],
            "years_experience": row["years_experience"],
            "theme": row["theme"],
            "question": row["question"],
            "lore": row["lore"],
            "tags": row["tags"].split(","),
            "created_at": row["created_at"]
        }
        for row in rows
    ]
@app.get("/professions")
def list_professions():
    """Return all professions and their entry counts."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute("""
        SELECT profession, COUNT(*) AS count
        FROM lore
        GROUP BY profession
        ORDER BY count DESC
    """)

    rows = db_cursor.fetchall()

    conn.close()

    return [
        {
            "profession": row["profession"],
            "count": row["count"]
        }
        for row in rows
    ]
@app.get("/today")
def today():
    """Return today's featured wisdom."""

    conn = get_connection()
    db_cursor = conn.cursor()

    # Get all entries
    db_cursor.execute("SELECT * FROM lore")
    entries = db_cursor.fetchall()

    if not entries:
        conn.close()
        return {
            "message": "Lore has not collected any wisdom yet."
        }

    seed = date.today().toordinal()
    random.seed(seed)
    # Random quote
    quote_entry = random.choice(entries)

    # Theme of the day
    db_cursor.execute("""
        SELECT theme, COUNT(*) AS count
        FROM lore
        GROUP BY theme
        ORDER BY RANDOM()
        LIMIT 1
    """)
    theme_row = db_cursor.fetchone()

    # Profession spotlight
    db_cursor.execute("""
        SELECT profession, COUNT(*) AS count
        FROM lore
        GROUP BY profession
        ORDER BY RANDOM()
        LIMIT 1
    """)
    profession_row = db_cursor.fetchone()

    conn.close()

    return {
        "today_quote": quote_entry["lore"],
        "person": quote_entry["person"],
        "theme_of_the_day": theme_row["theme"],
        "profession_spotlight": profession_row["profession"]
    }
@app.get("/recent")
def recent(limit: int = 20):
    """Return the most recent entries."""

    conn = get_connection()
    db_cursor = conn.cursor()

    db_cursor.execute("""
        SELECT *
        FROM lore
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = db_cursor.fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "person": row["person"],
            "profession": row["profession"],
            "years_experience": row["years_experience"],
            "theme": row["theme"],
            "question": row["question"],
            "lore": row["lore"],
            "tags": row["tags"].split(","),
            "created_at": row["created_at"]
        }
        for row in rows
    ]
@app.get("/health")
def health():
    """Application health check."""

    return {
        "status": "ok",
        "database": DB_NAME,
        "version": "0.9"
    }

"""
Apple Books Clone - Database Module
Handles all SQLite database operations for books and collections.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "books.db")

# Connection pool (simple singleton for SQLite)
_connection = None


@contextmanager
def get_connection():
    """Get database connection with automatic cleanup."""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    try:
        yield _connection
    except Exception:
        _connection.rollback()
        raise


def init_database():
    """Initialize the database with required tables and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT DEFAULT 'Unknown',
                file_path TEXT NOT NULL UNIQUE,
                file_type TEXT NOT NULL,
                cover_image BLOB,
                description TEXT,
                genre TEXT DEFAULT 'General',
                total_pages INTEGER DEFAULT 0,
                current_page INTEGER DEFAULT 0,
                progress REAL DEFAULT 0.0,
                is_favorite INTEGER DEFAULT 0,
                want_to_read INTEGER DEFAULT 0,
                finished INTEGER DEFAULT 0,
                date_added TEXT NOT NULL,
                last_read TEXT,
                collection_id INTEGER,
                FOREIGN KEY (collection_id) REFERENCES collections(id)
            )
        """)
        
        # Add indexes for frequently queried columns
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_date_added ON books(date_added DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_is_favorite ON books(is_favorite)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_progress ON books(progress)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_want_to_read ON books(want_to_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_finished ON books(finished)")
        
        # Add new columns if they don't exist (migration)
        try:
            cursor.execute("ALTER TABLE books ADD COLUMN want_to_read INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            cursor.execute("ALTER TABLE books ADD COLUMN finished INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT DEFAULT '📚',
                date_created TEXT NOT NULL
            )
        """)
        
        # Create default collections
        default_collections = [
            ("All Books", "📚"),
            ("Want to Read", "📖"),
            ("Currently Reading", "📕"),
            ("Finished", "✅"),
            ("Favorites", "❤️")
        ]
        
        for name, icon in default_collections:
            cursor.execute("""
                INSERT OR IGNORE INTO collections (name, icon, date_created)
                VALUES (?, ?, ?)
            """, (name, icon, datetime.now().isoformat()))
        
        conn.commit()


def add_book(title: str, author: str, file_path: str, file_type: str,
             cover_image: bytes = None, description: str = "", 
             genre: str = "General", total_pages: int = 0) -> int:
    """Add a new book to the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO books (title, author, file_path, file_type, cover_image,
                              description, genre, total_pages, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, author, file_path, file_type, cover_image, description,
              genre, total_pages, datetime.now().isoformat()))
        
        book_id = cursor.lastrowid
        conn.commit()
        return book_id


def get_all_books() -> List[Dict]:
    """Get all books from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY date_added DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_book_by_id(book_id: int) -> Optional[Dict]:
    """Get a single book by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_currently_reading() -> List[Dict]:
    """Get books that are currently being read (progress > 0 and < 100)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM books 
            WHERE progress > 0 AND progress < 100 
            ORDER BY last_read DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_recent_books(limit: int = 10) -> List[Dict]:
    """Get recently added books."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM books ORDER BY date_added DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def update_reading_progress(book_id: int, current_page: int, total_pages: int):
    """Update reading progress for a book."""
    progress = (current_page / total_pages * 100) if total_pages > 0 else 0
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE books 
            SET current_page = ?, total_pages = ?, progress = ?, last_read = ?
            WHERE id = ?
        """, (current_page, total_pages, progress, datetime.now().isoformat(), book_id))
        conn.commit()


def toggle_favorite(book_id: int) -> bool:
    """Toggle favorite status for a book."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_favorite FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        new_status = 0 if row['is_favorite'] else 1
        cursor.execute("UPDATE books SET is_favorite = ? WHERE id = ?", (new_status, book_id))
        conn.commit()
        return bool(new_status)


def get_favorites() -> List[Dict]:
    """Get all favorite books."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE is_favorite = 1 ORDER BY title")
        return [dict(row) for row in cursor.fetchall()]


def get_want_to_read() -> List[Dict]:
    """Get books marked as 'want to read'."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE want_to_read = 1 ORDER BY date_added DESC")
        return [dict(row) for row in cursor.fetchall()]


def toggle_want_to_read(book_id: int) -> bool:
    """Toggle 'want to read' status for a book."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT want_to_read FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        new_status = 0 if row['want_to_read'] else 1
        cursor.execute("UPDATE books SET want_to_read = ? WHERE id = ?", (new_status, book_id))
        conn.commit()
        return bool(new_status)


def get_finished() -> List[Dict]:
    """Get finished books."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE finished = 1 ORDER BY last_read DESC")
        return [dict(row) for row in cursor.fetchall()]


def toggle_finished(book_id: int) -> bool:
    """Toggle finished status for a book."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT finished FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        new_status = 0 if row['finished'] else 1
        cursor.execute("UPDATE books SET finished = ? WHERE id = ?", (new_status, book_id))
        conn.commit()
        return bool(new_status)


def delete_book(book_id: int):
    """Delete a book from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()


def get_all_collections() -> List[Dict]:
    """Get all collections."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM collections ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]


def search_books(query: str) -> List[Dict]:
    """Search books by title or author."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ?
            ORDER BY title
        """, (f"%{query}%", f"%{query}%"))
        return [dict(row) for row in cursor.fetchall()]

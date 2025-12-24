"""
Apple Books Clone - Database Module
Handles all SQLite database operations for books and collections.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "books.db")


def get_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with required tables."""
    conn = get_connection()
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
            date_added TEXT NOT NULL,
            last_read TEXT,
            collection_id INTEGER,
            FOREIGN KEY (collection_id) REFERENCES collections(id)
        )
    """)
    
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
    conn.close()


def add_book(title: str, author: str, file_path: str, file_type: str,
             cover_image: bytes = None, description: str = "", 
             genre: str = "General", total_pages: int = 0) -> int:
    """Add a new book to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO books (title, author, file_path, file_type, cover_image,
                          description, genre, total_pages, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, author, file_path, file_type, cover_image, description,
          genre, total_pages, datetime.now().isoformat()))
    
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return book_id


def get_all_books() -> List[Dict]:
    """Get all books from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books ORDER BY date_added DESC")
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return books


def get_book_by_id(book_id: int) -> Optional[Dict]:
    """Get a single book by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_currently_reading() -> List[Dict]:
    """Get books that are currently being read (progress > 0 and < 100)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM books 
        WHERE progress > 0 AND progress < 100 
        ORDER BY last_read DESC
    """)
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return books


def get_recent_books(limit: int = 10) -> List[Dict]:
    """Get recently added books."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM books ORDER BY date_added DESC LIMIT ?
    """, (limit,))
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return books


def update_reading_progress(book_id: int, current_page: int, total_pages: int):
    """Update reading progress for a book."""
    progress = (current_page / total_pages * 100) if total_pages > 0 else 0
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE books 
        SET current_page = ?, total_pages = ?, progress = ?, last_read = ?
        WHERE id = ?
    """, (current_page, total_pages, progress, datetime.now().isoformat(), book_id))
    conn.commit()
    conn.close()


def toggle_favorite(book_id: int) -> bool:
    """Toggle favorite status for a book."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    new_status = 0 if row['is_favorite'] else 1
    cursor.execute("UPDATE books SET is_favorite = ? WHERE id = ?", (new_status, book_id))
    conn.commit()
    conn.close()
    return bool(new_status)


def get_favorites() -> List[Dict]:
    """Get all favorite books."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE is_favorite = 1 ORDER BY title")
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return books


def delete_book(book_id: int):
    """Delete a book from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def get_all_collections() -> List[Dict]:
    """Get all collections."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM collections ORDER BY id")
    collections = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return collections


def search_books(query: str) -> List[Dict]:
    """Search books by title or author."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ?
        ORDER BY title
    """, (f"%{query}%", f"%{query}%"))
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return books


# Initialize database on module import
init_database()

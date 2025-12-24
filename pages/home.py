"""
Apple Books Clone - Home Page (Reading Now)
Shows currently reading books with progress.
"""

import customtkinter as ctk
from components.book_card import BookCard
import database


class HomePage(ctk.CTkScrollableFrame):
    """Reading Now page showing current reading progress."""
    
    def __init__(self, parent, on_open_book):
        super().__init__(parent, fg_color="transparent")
        self.on_open_book = on_open_book
        self._create_widgets()
    
    def _create_widgets(self):
        """Create page widgets."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="Reading Now",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        title.pack(anchor="w")
        
        # Currently reading section
        reading_books = database.get_currently_reading()
        
        if reading_books:
            self._create_section("Continue Reading", reading_books)
        else:
            # Empty state
            empty_frame = ctk.CTkFrame(self, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=50)
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📖",
                font=ctk.CTkFont(size=64)
            )
            empty_icon.pack(pady=(50, 20))
            
            empty_text = ctk.CTkLabel(
                empty_frame,
                text="No books in progress",
                font=ctk.CTkFont(size=18),
                text_color=("#86868B", "#86868B")
            )
            empty_text.pack()
            
            hint_text = ctk.CTkLabel(
                empty_frame,
                text="Import books from the Book Store to get started",
                font=ctk.CTkFont(size=14),
                text_color=("#86868B", "#86868B")
            )
            hint_text.pack(pady=(5, 0))
        
        # Recent additions section
        recent_books = database.get_recent_books(8)
        if recent_books:
            self._create_section("Recently Added", recent_books)
    
    def _create_section(self, title: str, books: list):
        """Create a section with books grid."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", padx=30, pady=(20, 10))
        
        # Section title
        section_title = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        section_title.pack(anchor="w", pady=(0, 15))
        
        # Books grid
        grid = ctk.CTkFrame(section, fg_color="transparent")
        grid.pack(fill="x")
        
        for i, book in enumerate(books):
            card = BookCard(grid, book, on_click=self.on_open_book, size="medium")
            card.grid(row=i // 5, column=i % 5, padx=10, pady=10, sticky="nw")
    
    def refresh(self):
        """Refresh the page content."""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()

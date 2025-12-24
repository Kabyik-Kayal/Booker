"""
Apple Books Clone - Library Page
Shows all books organized in collections.
"""

import customtkinter as ctk
from components.book_card import BookCard
import database


class LibraryPage(ctk.CTkScrollableFrame):
    """Library page showing all books and collections."""
    
    def __init__(self, parent, on_open_book):
        super().__init__(parent, fg_color="transparent")
        self.on_open_book = on_open_book
        self.current_filter = "all"
        self.search_query = ""
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create page widgets."""
        # Header with search
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="Library",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        title.pack(side="left")
        
        # Search bar
        self.search_entry = ctk.CTkEntry(
            header,
            width=250,
            height=36,
            placeholder_text="🔍 Search books...",
            font=ctk.CTkFont(size=14),
            corner_radius=18,
            border_width=1,
            border_color=("#D1D1D6", "#3A3A3C")
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Filter tabs
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        filters = [
            ("all", "All Books"),
            ("epub", "EPUBs"),
            ("pdf", "PDFs"),
        ]
        
        self.filter_buttons = {}
        for filter_id, label in filters:
            btn = ctk.CTkButton(
                filter_frame,
                text=label,
                width=100,
                height=32,
                corner_radius=16,
                font=ctk.CTkFont(size=13),
                fg_color="transparent" if filter_id != "all" else ("#007AFF", "#0A84FF"),
                text_color=("#1D1D1F", "#F5F5F7"),
                hover_color=("#E8E8ED", "#2C2C2E"),
                command=lambda f=filter_id: self._apply_filter(f)
            )
            btn.pack(side="left", padx=(0, 8))
            self.filter_buttons[filter_id] = btn
        
        # Books grid container
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=30)
        
        self._load_books()
    
    def _load_books(self):
        """Load and display books."""
        # Clear existing
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        
        # Get books
        if self.search_query:
            books = database.search_books(self.search_query)
        else:
            books = database.get_all_books()
        
        # Apply filter
        if self.current_filter == "epub":
            books = [b for b in books if b["file_type"].lower() == "epub"]
        elif self.current_filter == "pdf":
            books = [b for b in books if b["file_type"].lower() == "pdf"]
        
        if not books:
            # Empty state
            empty_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
            empty_frame.pack(expand=True, pady=100)
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📚",
                font=ctk.CTkFont(size=64)
            )
            empty_icon.pack(pady=(0, 20))
            
            message = "No books found" if self.search_query else "Your library is empty"
            empty_text = ctk.CTkLabel(
                empty_frame,
                text=message,
                font=ctk.CTkFont(size=18),
                text_color=("#86868B", "#86868B")
            )
            empty_text.pack()
            
            if not self.search_query:
                hint = ctk.CTkLabel(
                    empty_frame,
                    text="Go to Book Store to import your books",
                    font=ctk.CTkFont(size=14),
                    text_color=("#86868B", "#86868B")
                )
                hint.pack(pady=(5, 0))
            return
        
        # Create grid
        grid = ctk.CTkFrame(self.grid_container, fg_color="transparent")
        grid.pack(fill="x")
        
        # Book count
        count_label = ctk.CTkLabel(
            grid,
            text=f"{len(books)} books",
            font=ctk.CTkFont(size=13),
            text_color=("#86868B", "#86868B")
        )
        count_label.grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 15))
        
        for i, book in enumerate(books):
            card = BookCard(grid, book, on_click=self.on_open_book, size="medium")
            card.grid(row=(i // 5) + 1, column=i % 5, padx=10, pady=10, sticky="nw")
    
    def _on_search(self, event):
        """Handle search input."""
        self.search_query = self.search_entry.get().strip()
        self._load_books()
    
    def _apply_filter(self, filter_id: str):
        """Apply a filter to the books."""
        self.current_filter = filter_id
        
        # Update button states
        for fid, btn in self.filter_buttons.items():
            if fid == filter_id:
                btn.configure(fg_color=("#007AFF", "#0A84FF"))
            else:
                btn.configure(fg_color="transparent")
        
        self._load_books()
    
    def refresh(self):
        """Refresh the page."""
        self._load_books()

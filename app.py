"""
Apple Books Clone - Main Application
Entry point and main window configuration.
"""

import customtkinter as ctk
from components.sidebar import Sidebar
from pages.home import HomePage
from pages.library import LibraryPage
from pages.store import StorePage
from pages.reader import ReaderPage
import database


class AppleBooksApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Books")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Set appearance
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Configure window colors
        self.configure(fg_color=("#FFFFFF", "#1C1C1E"))
        
        # Initialize database
        database.init_database()
        
        # Create main layout
        self._create_layout()
        
        # Show home page by default
        self._navigate("home")
    
    def _create_layout(self):
        """Create the main application layout."""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = Sidebar(self.main_container, on_navigate=self._navigate)
        self.sidebar.pack(side="left", fill="y")
        
        # Content area
        self.content_area = ctk.CTkFrame(
            self.main_container,
            fg_color=("#FFFFFF", "#1C1C1E"),
            corner_radius=0
        )
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # Create pages
        self.pages = {}
        self._create_pages()
        
        # Reader page (overlay - not in pages dict initially)
        self.reader_page = ReaderPage(self, on_back=self._close_reader)
    
    def _create_pages(self):
        """Create all application pages."""
        self.pages["home"] = HomePage(self.content_area, on_open_book=self._open_book)
        self.pages["library"] = LibraryPage(self.content_area, on_open_book=self._open_book)
        self.pages["store"] = StorePage(self.content_area, on_import_complete=self._on_import)
        
        # Hide all pages initially
        for page in self.pages.values():
            page.pack_forget()
    
    def _navigate(self, page_id: str):
        """Navigate to a page."""
        # Handle collection pages
        if page_id in ["favorites", "want_to_read", "finished"]:
            self._show_collection(page_id)
            return
        
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show requested page
        if page_id in self.pages:
            self.pages[page_id].pack(fill="both", expand=True)
            
            # Refresh page content
            if hasattr(self.pages[page_id], 'refresh'):
                self.pages[page_id].refresh()
    
    def _show_collection(self, collection_id: str):
        """Show a collection view."""
        # For now, navigate to library with filter
        self._navigate("library")
    
    def _open_book(self, book_data: dict):
        """Open a book in the reader."""
        # Hide main container completely
        self.main_container.pack_forget()
        
        # Show reader filling full window
        self.reader_page.pack(fill="both", expand=True)
        self.reader_page.load_book(book_data)
    
    def _close_reader(self):
        """Close the reader and return to library."""
        self.reader_page.pack_forget()
        
        # Restore main container
        self.main_container.pack(fill="both", expand=True)
        
        # Refresh current page
        self._navigate("library")
    
    def _on_import(self):
        """Handle book import completion."""
        # Refresh pages
        if "home" in self.pages:
            self.pages["home"].refresh()
        if "library" in self.pages:
            self.pages["library"].refresh()


def main():
    """Run the application."""
    app = AppleBooksApp()
    app.mainloop()


if __name__ == "__main__":
    main()

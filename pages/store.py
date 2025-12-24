"""
Apple Books Clone - Store Page
Import and manage books (EPUB and PDF).
"""

import customtkinter as ctk
from tkinter import filedialog
import os
import database
from ebooklib import epub
import fitz  # PyMuPDF


class StorePage(ctk.CTkScrollableFrame):
    """Book Store page for importing books."""
    
    def __init__(self, parent, on_import_complete):
        super().__init__(parent, fg_color="transparent")
        self.on_import_complete = on_import_complete
        self._create_widgets()
    
    def _create_widgets(self):
        """Create page widgets."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        title = ctk.CTkLabel(
            header,
            text="Book Store",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Import your EPUB and PDF books",
            font=ctk.CTkFont(size=14),
            text_color=("#86868B", "#86868B")
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Import section
        import_section = ctk.CTkFrame(
            self,
            fg_color=("#FFFFFF", "#2C2C2E"),
            corner_radius=16,
            border_width=1,
            border_color=("#E5E5EA", "#3A3A3C")
        )
        import_section.pack(fill="x", padx=30, pady=20)
        
        # Import content
        import_content = ctk.CTkFrame(import_section, fg_color="transparent")
        import_content.pack(padx=40, pady=40)
        
        # Import icon
        import_icon = ctk.CTkLabel(
            import_content,
            text="📥",
            font=ctk.CTkFont(size=48)
        )
        import_icon.pack(pady=(0, 15))
        
        import_title = ctk.CTkLabel(
            import_content,
            text="Import Books",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        import_title.pack()
        
        import_desc = ctk.CTkLabel(
            import_content,
            text="Add EPUB or PDF files from your computer",
            font=ctk.CTkFont(size=14),
            text_color=("#86868B", "#86868B")
        )
        import_desc.pack(pady=(5, 20))
        
        # Import buttons
        buttons_frame = ctk.CTkFrame(import_content, fg_color="transparent")
        buttons_frame.pack()
        
        epub_btn = ctk.CTkButton(
            buttons_frame,
            text="📖 Import EPUB",
            width=150,
            height=44,
            corner_radius=22,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#007AFF", "#0A84FF"),
            hover_color=("#0056B3", "#0066CC"),
            command=self._import_epub
        )
        epub_btn.pack(side="left", padx=10)
        
        pdf_btn = ctk.CTkButton(
            buttons_frame,
            text="📄 Import PDF",
            width=150,
            height=44,
            corner_radius=22,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#FF3B30", "#FF453A"),
            hover_color=("#CC2F26", "#CC372E"),
            command=self._import_pdf
        )
        pdf_btn.pack(side="left", padx=10)
        
        # Supported formats info
        formats_frame = ctk.CTkFrame(self, fg_color="transparent")
        formats_frame.pack(fill="x", padx=30, pady=20)
        
        formats_title = ctk.CTkLabel(
            formats_frame,
            text="Supported Formats",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        formats_title.pack(anchor="w", pady=(0, 15))
        
        # Format cards
        formats_grid = ctk.CTkFrame(formats_frame, fg_color="transparent")
        formats_grid.pack(fill="x")
        
        self._create_format_card(formats_grid, "📖", "EPUB", 
            "Standard e-book format with reflowable text, chapters, and metadata support.", 0)
        self._create_format_card(formats_grid, "📄", "PDF",
            "Portable Document Format with fixed layout, images, and page navigation.", 1)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=("#34C759", "#30D158")
        )
        self.status_label.pack(pady=20)
    
    def _create_format_card(self, parent, icon: str, title: str, desc: str, col: int):
        """Create a format info card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=("#F5F5F7", "#1C1C1E"),
            corner_radius=12,
            width=280
        )
        card.grid(row=0, column=col, padx=(0, 15), pady=5, sticky="nsew")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=20, pady=20)
        
        icon_label = ctk.CTkLabel(
            content,
            text=icon,
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(anchor="w")
        
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        title_label.pack(anchor="w", pady=(10, 5))
        
        desc_label = ctk.CTkLabel(
            content,
            text=desc,
            font=ctk.CTkFont(size=12),
            text_color=("#86868B", "#86868B"),
            wraplength=240,
            justify="left"
        )
        desc_label.pack(anchor="w")
    
    def _import_epub(self):
        """Import EPUB files."""
        files = filedialog.askopenfilenames(
            title="Select EPUB files",
            filetypes=[("EPUB files", "*.epub")]
        )
        
        if files:
            imported = 0
            for file_path in files:
                try:
                    self._process_epub(file_path)
                    imported += 1
                except Exception as e:
                    print(f"Error importing {file_path}: {e}")
            
            if imported > 0:
                self.status_label.configure(
                    text=f"✓ Successfully imported {imported} EPUB file(s)",
                    text_color=("#34C759", "#30D158")
                )
                self.on_import_complete()
    
    def _import_pdf(self):
        """Import PDF files."""
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if files:
            imported = 0
            for file_path in files:
                try:
                    self._process_pdf(file_path)
                    imported += 1
                except Exception as e:
                    print(f"Error importing {file_path}: {e}")
            
            if imported > 0:
                self.status_label.configure(
                    text=f"✓ Successfully imported {imported} PDF file(s)",
                    text_color=("#34C759", "#30D158")
                )
                self.on_import_complete()
    
    def _process_epub(self, file_path: str):
        """Process and add EPUB to database."""
        book = epub.read_epub(file_path)
        
        # Extract metadata
        title = book.get_metadata('DC', 'title')
        title = title[0][0] if title else os.path.basename(file_path).replace('.epub', '')
        
        author = book.get_metadata('DC', 'creator')
        author = author[0][0] if author else "Unknown Author"
        
        description = book.get_metadata('DC', 'description')
        description = description[0][0] if description else ""
        
        # Extract cover image using multiple methods
        cover_image = None
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        
        # Method 1: Look for item with 'cover' in name
        for item in book.get_items():
            item_name = (item.get_name() or '').lower()
            media_type = item.media_type or ''
            
            # Check if it's an image
            is_image = media_type.startswith('image/') or item_name.endswith(image_extensions)
            
            if is_image and 'cover' in item_name:
                try:
                    cover_image = item.get_content()
                    break
                except Exception:
                    pass
        
        # Method 2: If no cover found, look for first image with 'cover' in any attribute
        if cover_image is None:
            for item in book.get_items():
                media_type = item.media_type or ''
                if media_type.startswith('image/'):
                    try:
                        cover_image = item.get_content()
                        break  # Use first image as fallback cover
                    except Exception:
                        pass
        
        # Count chapters (document items)
        total_pages = 0
        for item in book.get_items():
            if item.get_type() == 9:  # DOCUMENT type
                total_pages += 1
        if total_pages == 0:
            total_pages = len(list(book.get_items()))
        
        database.add_book(
            title=title,
            author=author,
            file_path=file_path,
            file_type="epub",
            cover_image=cover_image,
            description=description,
            total_pages=total_pages
        )
    
    def _process_pdf(self, file_path: str):
        """Process and add PDF to database."""
        doc = fitz.open(file_path)
        
        # Extract metadata
        metadata = doc.metadata
        title = metadata.get('title', '') or os.path.basename(file_path).replace('.pdf', '')
        author = metadata.get('author', '') or "Unknown Author"
        
        # Get page count
        total_pages = doc.page_count
        
        # Extract first page as cover
        cover_image = None
        if total_pages > 0:
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            cover_image = pix.tobytes("png")
        
        doc.close()
        
        database.add_book(
            title=title,
            author=author,
            file_path=file_path,
            file_type="pdf",
            cover_image=cover_image,
            total_pages=total_pages
        )

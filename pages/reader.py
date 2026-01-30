"""
Apple Books Clone - Reader Page
Full-featured book reader with two-page spread layout like real books.
"""

import customtkinter as ctk
from ebooklib import epub
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from PIL import Image
import io
import tkinter as tk
from tkinter import font
from functools import lru_cache
import webbrowser
import database


class ReaderPage(ctk.CTkFrame):
    """Book reader with authentic two-page spread layout."""
    
    # Cache for font metrics
    _font_cache = {}
    
    def __init__(self, parent, on_back):
        super().__init__(parent, fg_color=("#FAFAFA", "#1C1C1E"))
        self.on_back = on_back
        self.book_data = None
        self.current_page = 0
        self.total_pages = 0
        self.pages = []  # Paginated content
        self.pdf_doc = None
        self.font_size = 18
        self.line_height = 1.6
        self.font_family = "Georgia"
        self.file_type = ""
        
        # Store structured content (paragraphs) instead of raw text string
        self.structured_content = []
        
        # Table of Contents data
        self.toc_entries = []  # List of {title, page_index}
        self.toc_visible = False
        
        # Image cache for EPUB images
        self._image_cache = {}
        
        # PDF page cache for rendered pages
        self._pdf_page_cache = {}
        
        self._create_widgets()
        self.bind("<Configure>", self._on_resize)
    
    def _create_widgets(self):
        """Create reader widgets."""
        # Top toolbar - seamless design
        self.toolbar = ctk.CTkFrame(
            self,
            height=52,
            fg_color=("#FAFAFA", "#1C1C1E"),
            corner_radius=0
        )
        self.toolbar.pack(fill="x")
        self.toolbar.pack_propagate(False)
        
        # Back button
        back_btn = ctk.CTkButton(
            self.toolbar,
            text="← Library",
            width=100,
            height=36,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=("#007AFF", "#0A84FF"),
            hover_color=("#E8E8ED", "#3A3A3C"),
            command=self._on_back
        )
        back_btn.pack(side="left", padx=20, pady=10)
        
        # Book title (center)
        self.title_label = ctk.CTkLabel(
            self.toolbar,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        self.title_label.pack(side="left", expand=True)
        
        # Right side controls
        controls = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        controls.pack(side="right", padx=20)
        
        # Index/TOC button
        self.toc_btn = ctk.CTkButton(
            controls,
            text="☰",
            width=36,
            height=36,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            text_color=("#007AFF", "#0A84FF"),
            hover_color=("#E8E8ED", "#3A3A3C"),
            corner_radius=8,
            command=self._toggle_toc
        )
        self.toc_btn.pack(side="left", padx=(0, 10))
        
        # Font size controls
        font_smaller = ctk.CTkButton(
            controls,
            text="A",
            width=36,
            height=36,
            font=ctk.CTkFont(size=12),
            fg_color=("#E8E8ED", "#3A3A3C"),
            text_color=("#1D1D1F", "#F5F5F7"),
            hover_color=("#D1D1D6", "#4A4A4C"),
            corner_radius=8,
            command=self._decrease_font
        )
        font_smaller.pack(side="left", padx=2)
        
        font_larger = ctk.CTkButton(
            controls,
            text="A",
            width=36,
            height=36,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=("#E8E8ED", "#3A3A3C"),
            text_color=("#1D1D1F", "#F5F5F7"),
            hover_color=("#D1D1D6", "#4A4A4C"),
            corner_radius=8,
            command=self._increase_font
        )
        font_larger.pack(side="left", padx=2)
        
        # Favorite button
        self.fav_btn = ctk.CTkButton(
            controls,
            text="♡",
            width=36,
            height=36,
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            text_color=("#FF3B30", "#FF453A"),
            hover_color=("#E8E8ED", "#3A3A3C"),
            command=self._toggle_favorite
        )
        self.fav_btn.pack(side="left", padx=(10, 0))
        
        # Main book area - clean seamless background
        self.book_container = ctk.CTkFrame(
            self,
            fg_color=("#FAFAFA", "#1C1C1E"),
            corner_radius=0
        )
        self.book_container.pack(fill="both", expand=True)
        
        # Table of Contents Panel (hidden by default)
        self.toc_panel = ctk.CTkFrame(
            self.book_container,
            width=280,
            fg_color=("#FFFFFF", "#2C2C2E"),
            corner_radius=0
        )
        # Don't pack yet - will be shown/hidden with _toggle_toc
        
        # TOC Header
        toc_header = ctk.CTkFrame(self.toc_panel, fg_color="transparent", height=50)
        toc_header.pack(fill="x", padx=16, pady=(16, 8))
        toc_header.pack_propagate(False)
        
        ctk.CTkLabel(
            toc_header,
            text="Contents",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        ).pack(side="left", pady=10)
        
        # Close button for TOC
        ctk.CTkButton(
            toc_header,
            text="✕",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=("#8E8E93", "#8E8E93"),
            hover_color=("#E5E5EA", "#3A3A3C"),
            corner_radius=15,
            command=self._toggle_toc
        ).pack(side="right")
        
        # Scrollable TOC list
        self.toc_scrollable = ctk.CTkScrollableFrame(
            self.toc_panel,
            fg_color="transparent",
            scrollbar_button_color=("#D1D1D6", "#48484A"),
            scrollbar_button_hover_color=("#B0B0B5", "#5A5A5C")
        )
        self.toc_scrollable.pack(fill="both", expand=True, padx=8, pady=(0, 16))
        
        # Book spread (two pages side by side) - no gaps
        self.book_spread = ctk.CTkFrame(
            self.book_container,
            fg_color="transparent"
        )
        self.book_spread.pack(expand=True, fill="both", padx=0, pady=0)
        
        # Left page - clean borderless design
        self.left_page_frame = ctk.CTkFrame(
            self.book_spread,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=0,
            border_width=0
        )
        self.left_page_frame.pack(side="left", fill="both", expand=True)
        self.left_page_frame.pack_propagate(False)
        
        # Content area for mixed text/images
        self.left_page_content = ctk.CTkFrame(
            self.left_page_frame,
            fg_color="transparent"
        )
        self.left_page_content.pack(fill="both", expand=True, padx=40, pady=24)
        self.left_content_widgets = []
        
        self.left_page_num = ctk.CTkLabel(
            self.left_page_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("#98989D", "#6E6E73")
        )
        self.left_page_num.pack(side="bottom", pady=(0, 20))
        
        # Subtle center divider
        self.spine = ctk.CTkFrame(
            self.book_spread,
            width=1,
            fg_color=("#E5E5EA", "#38383A"),
            corner_radius=0
        )
        self.spine.pack(side="left", fill="y", pady=30)
        
        # Right page - clean borderless design
        self.right_page_frame = ctk.CTkFrame(
            self.book_spread,
            fg_color=("#FFFFFF", "#1E1E1E"),
            corner_radius=0,
            border_width=0
        )
        self.right_page_frame.pack(side="left", fill="both", expand=True)
        self.right_page_frame.pack_propagate(False)
        
        # Content area for mixed text/images
        self.right_page_content = ctk.CTkFrame(
            self.right_page_frame,
            fg_color="transparent"
        )
        self.right_page_content.pack(fill="both", expand=True, padx=40, pady=24)
        self.right_content_widgets = []
        
        self.right_page_num = ctk.CTkLabel(
            self.right_page_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("#98989D", "#6E6E73")
        )
        self.right_page_num.pack(side="bottom", pady=(0, 20))
        
        # PDF image labels (hidden by default)
        self.left_pdf_image = ctk.CTkLabel(
            self.left_page_content,
            text=""
        )
        self.right_pdf_image = ctk.CTkLabel(
            self.right_page_content,
            text=""
        )
        
        # Bottom navigation bar - minimal seamless design
        self.nav_bar = ctk.CTkFrame(
            self,
            height=64,
            fg_color=("#FAFAFA", "#1C1C1E"),
            corner_radius=0
        )
        self.nav_bar.pack(fill="x", side="bottom")
        self.nav_bar.pack_propagate(False)
        
        nav_content = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        nav_content.pack(expand=True)
        
        # Previous button - subtle rounded style
        self.prev_btn = ctk.CTkButton(
            nav_content,
            text="‹",
            width=44,
            height=44,
            font=ctk.CTkFont(size=28),
            fg_color="transparent",
            text_color=("#8E8E93", "#8E8E93"),
            hover_color=("#E5E5EA", "#38383A"),
            corner_radius=22,
            command=self._prev_page
        )
        self.prev_btn.pack(side="left", padx=20)
        
        # Progress container
        progress_frame = ctk.CTkFrame(nav_content, fg_color="transparent")
        progress_frame.pack(side="left", padx=20)
        
        # Progress slider - minimal thin design
        self.progress_slider = ctk.CTkSlider(
            progress_frame,
            width=480,
            height=16,
            from_=0,
            to=100,
            number_of_steps=100,
            progress_color=("#FF9500", "#FF9F0A"),
            button_color=("#FFFFFF", "#FFFFFF"),
            button_hover_color=("#F5F5F5", "#E8E8E8"),
            fg_color=("#E5E5EA", "#38383A"),
            command=self._on_slider_change
        )
        self.progress_slider.pack()
        self.progress_slider.set(0)
        
        # Page indicator
        self.page_label = ctk.CTkLabel(
            progress_frame,
            text="Page 0 of 0",
            font=ctk.CTkFont(size=12),
            text_color=("#86868B", "#86868B")
        )
        self.page_label.pack(pady=(5, 0))
        
        # Next button - subtle rounded style
        self.next_btn = ctk.CTkButton(
            nav_content,
            text="›",
            width=44,
            height=44,
            font=ctk.CTkFont(size=28),
            fg_color="transparent",
            text_color=("#8E8E93", "#8E8E93"),
            hover_color=("#E5E5EA", "#38383A"),
            corner_radius=22,
            command=self._next_page
        )
        self.next_btn.pack(side="left", padx=20)
        
        # Make the frame focusable for keyboard bindings
        self.book_container.bind("<Button-1>", lambda e: self.focus_set())
        self.bind("<Left>", lambda e: self._prev_page())
        self.bind("<Right>", lambda e: self._next_page())
        self.bind("<space>", lambda e: self._next_page())
    
    def _calculate_page_dimensions(self):
        """Calculate page dimensions to fill the screen."""
        try:
            window_height = self.winfo_height() - 140  # Subtract toolbar and navbar
            window_width = self.winfo_width()
            
            # Calculate available space for the two-page spread
            available_width = window_width - 60  # Small margin on sides
            available_height = window_height - 40  # Small margin top/bottom
            
            # Each page gets half the width minus spine
            page_width = int((available_width - 10) / 2)  # 10px for spine
            
            # Use the full available height
            page_height = available_height
            
            # Update page frames
            self.left_page_frame.configure(width=page_width, height=page_height)
            self.right_page_frame.configure(width=page_width, height=page_height)
            
            # Update wrap length for text - textboxes don't need wraplength
            # Just update the page dimensions
            
            return page_width, page_height
        except:
            return 500, 700
    
    def _on_resize(self, event=None):
        """Handle window resize."""
        if self.book_data and self.file_type == "epub":
            self._calculate_page_dimensions()
            # Debounce repagination for performance
            if hasattr(self, '_resize_job'):
                self.after_cancel(self._resize_job)
            self._resize_job = self.after(200, self._perform_resize_update)

    def _perform_resize_update(self):
        self._repaginate_epub()
        self._show_current_spread()
    
    def load_book(self, book_data: dict):
        """Load a book for reading."""
        self.book_data = book_data
        self.current_page = book_data.get("current_page", 0)
        self.title_label.configure(text=book_data.get("title", "Unknown"))
        
        # Update favorite button
        is_fav = book_data.get("is_favorite", 0)
        self.fav_btn.configure(text="❤️" if is_fav else "♡")
        
        self.file_type = book_data.get("file_type", "").lower()
        
        # Calculate dimensions first
        self.update_idletasks()
        self._calculate_page_dimensions()
        
        if self.file_type == "epub":
            self._load_epub(book_data["file_path"])
        elif self.file_type == "pdf":
            self._load_pdf(book_data["file_path"])
        
        self._show_current_spread()
    
    def _load_epub(self, file_path: str):
        """Load EPUB content with images."""
        # Show EPUB content areas, hide PDF image areas
        self.left_page_content.pack(fill="both", expand=True, padx=40, pady=24)
        self.right_page_content.pack(fill="both", expand=True, padx=40, pady=24)
        self.left_pdf_image.pack_forget()
        self.right_pdf_image.pack_forget()
        
        try:
            book = epub.read_epub(file_path)
            self.structured_content = []
            seen_texts = set()
            
            # Extract all images using MIME type and extension
            image_map = {}
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg')
            
            for item in book.get_items():
                item_name = item.get_name() or ''
                media_type = item.media_type or ''
                
                # Check if it's an image by MIME type or extension
                is_image = (
                    media_type.startswith('image/') or
                    item_name.lower().endswith(image_extensions)
                )
                
                if is_image:
                    try:
                        img_data = item.get_content()
                        img = Image.open(io.BytesIO(img_data))
                        img = img.convert('RGB')  # Ensure compatible format
                        image_map[item_name] = img
                    except Exception:
                        pass  # Skip failed images
            
            # Extract content with image references
            for item in book.get_items():
                if item.get_type() == 9:  # Document type
                    content = item.get_content().decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Process all elements in order
                    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'image', 'svg', 'a']):
                        if element.name in ['img', 'image']:
                            # Handle image - try multiple src attributes
                            img_src = element.get('src', '') or element.get('xlink:href', '') or element.get('href', '')
                            
                            if img_src:
                                # Extract just the filename for matching
                                img_filename = img_src.split('/')[-1].split('\\')[-1]
                                
                                # Try to find the image in our map
                                img_obj = None
                                for img_name, img in image_map.items():
                                    stored_filename = img_name.split('/')[-1].split('\\')[-1]
                                    if img_filename == stored_filename or img_filename in img_name:
                                        img_obj = img.copy()  # Copy to avoid issues
                                        break
                                
                                if img_obj:
                                    self.structured_content.append({
                                        'type': 'image',
                                        'image': img_obj,
                                        'is_header': False
                                    })
                                    # Cache the image
                                    self._image_cache[img_filename] = img_obj
                        elif element.name == 'svg':
                            # Skip SVG for now
                            continue
                        elif element.name == 'a':
                            # Handle links - standalone links with text
                            href = element.get('href', '')
                            link_text = element.get_text(strip=True)
                            if link_text and href and href.startswith(('http://', 'https://')):
                                if link_text not in seen_texts:
                                    seen_texts.add(link_text)
                                    self.structured_content.append({
                                        'type': 'link',
                                        'text': link_text,
                                        'url': href,
                                        'is_header': False,
                                        'header_level': 0
                                    })
                        else:
                            # Handle text (p, h1-h6)
                            text = element.get_text(strip=True)
                            if text and text not in seen_texts:
                                seen_texts.add(text)
                                is_header = element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
                                # Extract header level (1-6) for TOC hierarchy
                                header_level = int(element.name[1]) if is_header else 0
                                
                                # Check for embedded links in this element
                                links = []
                                for link in element.find_all('a'):
                                    link_href = link.get('href', '')
                                    link_text = link.get_text(strip=True)
                                    if link_href and link_text:
                                        links.append({'text': link_text, 'url': link_href})
                                
                                self.structured_content.append({
                                    'type': 'text',
                                    'text': text,
                                    'is_header': is_header,
                                    'header_level': header_level,
                                    'links': links
                                })
            
            # Extract TOC from EPUB
            self._extract_toc_from_epub(book)
            
            # Ensure window is updated before calculating pagination
            self.update_idletasks()
            self._repaginate_epub()
            
            # Update TOC page indices with actual pages and populate
            self._update_toc_page_indices()
            self._populate_toc()
            
        except Exception as e:
            self.pages = [[{'type': 'text', 'text': f"Error loading EPUB:\n{str(e)}"}]]
            self.total_pages = 1
    
    def _get_font(self, font_family, font_size, is_header=False):
        """Get or create a cached font object."""
        cache_key = (font_family, font_size, is_header)
        if cache_key not in self._font_cache:
            self._font_cache[cache_key] = font.Font(
                family=font_family, 
                size=font_size + (4 if is_header else 0),
                weight="bold" if is_header else "normal"
            )
        return self._font_cache[cache_key]
    
    def _measure_text_height(self, text, font_family, font_size, width, is_header=False):
        """
        Estimate height of text wrapped to a specific width using cached font metrics.
        """
        f = self._get_font(font_family, font_size, is_header)
        
        # Line height in pixels
        line_height = f.metrics('linespace')
        
        # Simple wrapping estimation
        # Total pixels wide
        text_pixels = f.measure(text)
        
        # Add a 8% margin for word wrap overhead
        num_lines = max(1, int((text_pixels * 1.08) / width) + 1)
        
        # Also account for explicit newlines
        newline_lines = text.count('\n') + 1
        num_lines = max(num_lines, newline_lines)
        
        return num_lines * line_height

    def _repaginate_epub(self):
        """
        Pixel-height based pagination.
        Fills pages consistently and prevents cut-offs.
        """
        if not self.structured_content:
            return
            
        self.pages = []
        page_width, page_height = self._calculate_page_dimensions()
        
        # Available vertical space - minimize margins to fill pages
        available_height = page_height - 50  # Just enough for page number
        wrap_width = page_width - 80  # Less horizontal padding too
        
        current_page_items = []
        current_height = 0
        
        # Tighter paragraph spacing
        p_spacing = 10
        
        for item in self.structured_content:
            is_header = item.get('is_header', False)
            
            if item['type'] == 'image':
                # Fixed estimation for images, will be resized to max 350
                img_h = 350 + 20 # img_h + pady
                
                if current_height + img_h > available_height and current_page_items:
                    self.pages.append(current_page_items)
                    current_page_items = [item]
                    current_height = img_h
                else:
                    current_page_items.append(item)
                    current_height += img_h
                    
            elif item['type'] == 'text':
                text = item['text']
                h = self._measure_text_height(text, self.font_family, self.font_size, wrap_width, is_header)
                
                if current_height + h + p_spacing <= available_height:
                    # Fits completely
                    current_page_items.append(item)
                    current_height += h + p_spacing
                else:
                    # Paragraph too long, split it by lines
                    remaining_text = text
                    f = self._get_font(self.font_family, self.font_size, is_header)
                    line_height = f.metrics('linespace')
                    
                    while remaining_text:
                        space_left = available_height - current_height
                        
                        # How many lines fit?
                        lines_that_fit = max(0, int(space_left / line_height))
                        
                        if lines_that_fit < 2 and current_page_items:
                            # Start new page if only 1-2 lines fit
                            self.pages.append(current_page_items)
                            current_page_items = []
                            current_height = 0
                            continue
                            
                        # Estimate characters per line - slightly more conservative
                        chars_per_line = int(wrap_width / (self.font_size * 0.42))
                        total_chars_that_fit = lines_that_fit * chars_per_line
                        
                        if len(remaining_text) <= total_chars_that_fit:
                            # Fits now
                            chunk_h = self._measure_text_height(remaining_text, self.font_family, self.font_size, wrap_width, is_header)
                            current_page_items.append({
                                'type': 'text',
                                'text': remaining_text,
                                'is_header': is_header
                            })
                            current_height += chunk_h + p_spacing
                            remaining_text = ""
                        else:
                            # Split by words
                            chunk = remaining_text[:total_chars_that_fit]
                            last_space = chunk.rfind(' ')
                            split_idx = last_space if last_space > total_chars_that_fit * 0.8 else total_chars_that_fit
                            
                            page_chunk = remaining_text[:split_idx].strip()
                            if page_chunk:
                                chunk_h = self._measure_text_height(page_chunk, self.font_family, self.font_size, wrap_width, is_header)
                                current_page_items.append({
                                    'type': 'text',
                                    'text': page_chunk,
                                    'is_header': is_header
                                })
                                current_height += chunk_h + p_spacing
                            
                            # Start new page
                            self.pages.append(current_page_items)
                            current_page_items = []
                            current_height = 0
                            remaining_text = remaining_text[split_idx:].strip()
        
        # Final page
        if current_page_items:
            self.pages.append(current_page_items)
            
        self.total_pages = len(self.pages) or 1
        self._update_navigation()

    def _load_pdf(self, file_path: str):
        """Load PDF content."""
        # Hide EPUB content areas, show PDF image areas
        self.left_page_content.pack_forget()
        self.right_page_content.pack_forget()
        self.left_pdf_image.pack(fill="both", expand=True)
        self.right_pdf_image.pack(fill="both", expand=True)
        
        # Clear cache when loading a new PDF
        self._pdf_page_cache.clear()
        
        try:
            if self.pdf_doc:
                self.pdf_doc.close()
            
            self.pdf_doc = fitz.open(file_path)
            self.total_pages = self.pdf_doc.page_count
            self.pages = list(range(self.total_pages))
            
        except Exception:
            self.total_pages = 0
            self.pages = []
        
        self._update_navigation()
    
    def _show_current_spread(self):
        """Display the current two-page spread."""
        if self.file_type == "epub":
            self._show_epub_spread()
        elif self.file_type == "pdf":
            self._show_pdf_spread()
        
        self._update_navigation()
        self._save_progress()
    
    def _show_epub_spread(self):
        """Show EPUB content with native widgets."""
        left_idx = self.current_page * 2
        right_idx = left_idx + 1
        
        # Display left page
        self._display_page_content(
            left_idx, 
            self.left_page_content, 
            self.left_content_widgets,
            self.left_page_num
        )
        
        # Display right page  
        self._display_page_content(
            right_idx,
            self.right_page_content,
            self.right_content_widgets, 
            self.right_page_num
        )
    
    def _display_page_content(self, page_idx, container, widget_list, page_num_label):
        """Display page content with native text and image widgets."""
        # Clear previous content
        for widget in widget_list:
            widget.destroy()
        widget_list.clear()
        
        if page_idx >= len(self.pages):
            page_num_label.configure(text="")
            return
        
        page_data = self.pages[page_idx]
        page_num_label.configure(text=str(page_idx + 1))
        
        # Get page width for wrapping - match pagination
        page_width, _ = self._calculate_page_dimensions()
        wrap_width = page_width - 80
        
        # Process page content items
        for item in page_data:
            if item['type'] == 'text':
                text = item['text']
                is_header = item.get('is_header', False)
                header_level = item.get('header_level', 0)
                
                # Calculate font size and style based on header level
                if is_header:
                    # h1 = largest, h6 = smallest
                    size_map = {1: 10, 2: 6, 3: 4, 4: 2, 5: 1, 6: 0}
                    font_size_delta = size_map.get(header_level, 0)
                    font_weight = "bold"
                    # h1/h2 = dark, h3+ = slightly lighter
                    if header_level <= 2:
                        text_color = ("#1D1D1F", "#F5F5F7")
                    else:
                        text_color = ("#48484A", "#C7C7CC")
                    spacing = 16 if header_level <= 2 else 12
                else:
                    font_size_delta = 0
                    font_weight = "normal"
                    text_color = ("#1D1D1F", "#F5F5F7")
                    spacing = 10
                
                # Create text label with improved formatting
                text_label = ctk.CTkLabel(
                    container,
                    text=text,
                    font=ctk.CTkFont(
                        family=self.font_family, 
                        size=self.font_size + font_size_delta,
                        weight=font_weight
                    ),
                    text_color=text_color,
                    wraplength=wrap_width,
                    justify="left",
                    anchor="nw"
                )
                text_label.pack(fill="x", anchor="w", pady=(0, spacing))
                widget_list.append(text_label)
                
            elif item['type'] == 'link':
                # Standalone clickable link
                link_text = item.get('text', 'Link')
                link_url = item.get('url', '')
                
                link_btn = ctk.CTkButton(
                    container,
                    text=f"🔗 {link_text}",
                    anchor="w",
                    height=32,
                    font=ctk.CTkFont(family=self.font_family, size=self.font_size - 1),
                    fg_color="transparent",
                    text_color=("#007AFF", "#0A84FF"),
                    hover_color=("#E5F1FF", "#1C3A5F"),
                    corner_radius=6,
                    command=lambda url=link_url: self._open_link(url)
                )
                link_btn.pack(fill="x", anchor="w", pady=(0, 8))
                widget_list.append(link_btn)
                
            elif item['type'] == 'image':
                try:
                    img = item['image']
                    # Resize image to fit page
                    max_width = wrap_width - 20
                    max_height = 350
                    
                    ratio = min(max_width / img.width, max_height / img.height, 1.0)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    
                    ctk_img = ctk.CTkImage(
                        light_image=img,
                        dark_image=img,
                        size=new_size
                    )
                    
                    img_label = ctk.CTkLabel(
                        container,
                        text="",
                        image=ctk_img
                    )
                    img_label._ctk_image = ctk_img  # Keep reference
                    img_label.pack(pady=20)
                    widget_list.append(img_label)
                except Exception:
                    pass  # Skip image display errors
    
    def _show_pdf_spread(self):
        """Show PDF page spread."""
        if not self.pdf_doc:
            return
        
        page_width, page_height = self._calculate_page_dimensions()
        
        # Left page
        left_idx = self.current_page * 2
        if left_idx < self.pdf_doc.page_count:
            self._render_pdf_page(left_idx, self.left_pdf_image, page_width - 80, page_height - 100)
            self.left_page_num.configure(text=str(left_idx + 1))
        else:
            self.left_pdf_image.configure(image=None, text="")
            self.left_page_num.configure(text="")
        
        # Right page
        right_idx = left_idx + 1
        if right_idx < self.pdf_doc.page_count:
            self._render_pdf_page(right_idx, self.right_pdf_image, page_width - 80, page_height - 100)
            self.right_page_num.configure(text=str(right_idx + 1))
        else:
            self.right_pdf_image.configure(image=None, text="")
            self.right_page_num.configure(text="")
    
    def _render_pdf_page(self, page_num: int, label: ctk.CTkLabel, max_width: int, max_height: int):
        """Render a PDF page to a label with caching."""
        # Check cache first
        cache_key = (page_num, max_width, max_height)
        if cache_key in self._pdf_page_cache:
            photo = self._pdf_page_cache[cache_key]
            label.configure(image=photo)
            label.image = photo
            return
        
        page = self.pdf_doc[page_num]
        
        # Calculate scale to fit
        rect = page.rect
        scale_w = max_width / rect.width
        scale_h = max_height / rect.height
        scale = min(scale_w, scale_h)
        
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        photo = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(int(rect.width * scale), int(rect.height * scale))
        )
        
        # Cache the rendered page (limit cache size to 20 pages)
        if len(self._pdf_page_cache) > 20:
            # Remove oldest entry
            self._pdf_page_cache.pop(next(iter(self._pdf_page_cache)))
        self._pdf_page_cache[cache_key] = photo
        
        label.configure(image=photo)
        label.image = photo  # Keep reference
    
    def _update_navigation(self):
        """Update navigation controls."""
        # Calculate spread count (two pages per spread)
        if self.file_type == "epub":
            total_spreads = (len(self.pages) + 1) // 2
            current_spread = self.current_page
        else:
            total_spreads = (self.total_pages + 1) // 2
            current_spread = self.current_page
        
        if total_spreads == 0:
            total_spreads = 1
        
        self.page_label.configure(
            text=f"Pages {self.current_page * 2 + 1}-{min(self.current_page * 2 + 2, self.total_pages)} of {self.total_pages}"
        )
        
        if total_spreads > 1:
            progress = (current_spread / (total_spreads - 1)) * 100
        else:
            progress = 100
        self.progress_slider.set(progress)
        
        # Enable/disable buttons
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_spreads - 1 else "disabled")
    
    def _prev_page(self):
        """Go to previous spread."""
        if self.current_page > 0:
            self.current_page -= 1
            self._show_current_spread()
    
    def _next_page(self):
        """Go to next spread."""
        if self.file_type == "epub":
            max_spread = (len(self.pages) + 1) // 2 - 1
        else:
            max_spread = (self.total_pages + 1) // 2 - 1
        
        if self.current_page < max_spread:
            self.current_page += 1
            self._show_current_spread()
    
    def _on_slider_change(self, value):
        """Handle slider change."""
        if self.file_type == "epub":
            total_spreads = (len(self.pages) + 1) // 2
        else:
            total_spreads = (self.total_pages + 1) // 2
        
        if total_spreads > 1:
            new_spread = int((value / 100) * (total_spreads - 1))
        else:
            new_spread = 0
        
        if new_spread != self.current_page:
            self.current_page = new_spread
            self._show_current_spread()
    
    def _save_progress(self):
        """Save reading progress."""
        if self.book_data:
            current = self.current_page * 2
            total = self.total_pages if self.file_type == "epub" else self.pdf_doc.page_count if self.pdf_doc else 0
            database.update_reading_progress(
                self.book_data["id"],
                current,
                total
            )
    
    def _decrease_font(self):
        """Decrease font size."""
        if self.font_size > 14:
            self.font_size -= 2
            self._update_font()
    
    def _increase_font(self):
        """Increase font size."""
        if self.font_size < 26:
            self.font_size += 2
            self._update_font()
    
    def _update_font(self):
        """Update font and repaginate."""
        # Just repaginate - widgets are recreated with new font on display
        if self.file_type == "epub":
            self._repaginate_epub()
            self.current_page = 0
            self._show_current_spread()
    
    def _toggle_favorite(self):
        """Toggle favorite status."""
        if self.book_data:
            is_fav = database.toggle_favorite(self.book_data["id"])
            self.fav_btn.configure(text="❤️" if is_fav else "♡")
            self.book_data["is_favorite"] = 1 if is_fav else 0
    
    def _open_link(self, url):
        """Open a link in the system's default web browser."""
        if url:
            try:
                webbrowser.open(url)
            except Exception:
                pass  # Silently handle errors
    
    def _on_back(self):
        """Handle back button."""
        if self.pdf_doc:
            self.pdf_doc.close()
            self.pdf_doc = None
        self.on_back()
    
    def _toggle_toc(self):
        """Toggle the Table of Contents panel visibility."""
        if self.toc_visible:
            self.toc_panel.pack_forget()
            self.toc_visible = False
        else:
            # Show TOC on the left side
            self.toc_panel.pack(side="left", fill="y", before=self.book_spread)
            self.toc_panel.pack_propagate(False)
            self.toc_visible = True
    
    def _populate_toc(self):
        """Populate the TOC panel with chapter entries."""
        # Clear existing entries
        for widget in self.toc_scrollable.winfo_children():
            widget.destroy()
        
        # Track expanded state for sections
        if not hasattr(self, '_toc_expanded'):
            self._toc_expanded = {}
        
        if not self.toc_entries:
            # No TOC found message
            ctk.CTkLabel(
                self.toc_scrollable,
                text="No chapters found",
                font=ctk.CTkFont(size=13),
                text_color=("#8E8E93", "#8E8E93")
            ).pack(pady=20)
            return
        
        # Create hierarchical TOC with dropdowns
        self._create_toc_items(self.toc_entries, self.toc_scrollable, 0)
    
    def _create_toc_items(self, entries, parent, depth):
        """Recursively create TOC items with collapsible children."""
        for i, entry in enumerate(entries):
            title = entry.get('title', f'Chapter {i + 1}')
            page_idx = entry.get('page_index', 0)
            children = entry.get('children', [])
            entry_id = f"{depth}_{i}_{title[:20]}"
            
            # Container for this item and its children
            item_container = ctk.CTkFrame(parent, fg_color="transparent")
            item_container.pack(fill="x")
            
            # Calculate indent
            indent = 16 * depth
            
            # Row frame for the item
            row_frame = ctk.CTkFrame(item_container, fg_color="transparent")
            row_frame.pack(fill="x", padx=(indent, 0))
            
            if children:
                # This item has children - add expand/collapse toggle
                is_expanded = self._toc_expanded.get(entry_id, False)
                toggle_text = "▼" if is_expanded else "▶"
                
                toggle_btn = ctk.CTkButton(
                    row_frame,
                    text=toggle_text,
                    width=24,
                    height=24,
                    font=ctk.CTkFont(size=10),
                    fg_color="transparent",
                    text_color=("#8E8E93", "#8E8E93"),
                    hover_color=("#E5E5EA", "#38383A"),
                    corner_radius=4,
                    command=lambda eid=entry_id, cont=item_container, ch=children, d=depth: 
                        self._toggle_toc_section(eid, cont, ch, d)
                )
                toggle_btn.pack(side="left", padx=(4, 0))
            else:
                # Spacer for alignment
                spacer = ctk.CTkFrame(row_frame, width=28, height=24, fg_color="transparent")
                spacer.pack(side="left")
            
            # Truncate long titles
            max_len = 32 - (depth * 3)
            display_title = title[:max_len] + "..." if len(title) > max_len + 3 else title
            
            # Title button
            title_btn = ctk.CTkButton(
                row_frame,
                text=display_title,
                anchor="w",
                height=36,
                font=ctk.CTkFont(size=14, weight="bold" if depth == 0 else "normal"),
                fg_color="transparent",
                text_color=("#1D1D1F", "#F5F5F7") if depth == 0 else ("#48484A", "#AEAEB2"),
                hover_color=("#E5E5EA", "#38383A"),
                corner_radius=8,
                command=lambda idx=page_idx: self._navigate_to_chapter(idx)
            )
            title_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
            
            # Children container (hidden by default)
            if children:
                children_frame = ctk.CTkFrame(item_container, fg_color="transparent")
                children_frame._toc_children = True  # Mark for identification
                
                if self._toc_expanded.get(entry_id, False):
                    children_frame.pack(fill="x")
                    self._create_toc_items(children, children_frame, depth + 1)
    
    def _toggle_toc_section(self, entry_id, container, children, depth):
        """Toggle a TOC section expanded/collapsed."""
        is_expanded = self._toc_expanded.get(entry_id, False)
        self._toc_expanded[entry_id] = not is_expanded
        
        # Rebuild the TOC to reflect changes
        self._populate_toc()
    
    def _navigate_to_chapter(self, page_index):
        """Navigate to a specific chapter/page."""
        # Convert page index to spread index
        spread_index = page_index // 2
        
        if self.file_type == "epub":
            max_spread = (len(self.pages) + 1) // 2 - 1
        else:
            max_spread = (self.total_pages + 1) // 2 - 1
        
        self.current_page = min(spread_index, max(0, max_spread))
        self._show_current_spread()
        
        # Close TOC panel after navigation
        if self.toc_visible:
            self._toggle_toc()
    
    def _extract_toc_from_epub(self, book):
        """Extract table of contents from EPUB."""
        self.toc_entries = []
        
        try:
            # Try to get TOC from EPUB
            toc = book.toc
            if toc:
                self._parse_toc_items(toc)
        except Exception:
            pass
        
        # If no TOC found, generate from headers
        if not self.toc_entries:
            self._generate_toc_from_headers()
    
    def _parse_toc_items(self, toc_items, depth=0):
        """Recursively parse TOC items into hierarchical structure."""
        result = []
        for item in toc_items:
            if isinstance(item, tuple):
                # Nested TOC (section, children)
                section, children = item
                if hasattr(section, 'title'):
                    entry = {
                        'title': section.title,
                        'page_index': len(self.toc_entries),
                        'depth': depth,
                        'children': []
                    }
                    self.toc_entries.append(entry)
                    if children:
                        entry['children'] = self._parse_toc_items(children, depth + 1)
            elif hasattr(item, 'title'):
                entry = {
                    'title': item.title,
                    'page_index': len(self.toc_entries),
                    'depth': depth,
                    'children': []
                }
                self.toc_entries.append(entry)
        return result
    
    def _generate_toc_from_headers(self):
        """Generate TOC from h1/h2/h3/h4 headers in content with hierarchy."""
        current_page = 0
        items_on_page = 0
        
        # Track hierarchy: h1 > h2 > h3 > h4
        current_h1 = None
        current_h2 = None
        current_h3 = None
        
        for i, item in enumerate(self.structured_content):
            if item['type'] == 'text' and item.get('is_header', False):
                text = item['text']
                header_level = item.get('header_level', 2)
                
                # Only include reasonably sized headers
                if len(text) < 80:
                    entry = {
                        'title': text,
                        'page_index': current_page,
                        'depth': 0,
                        'children': []
                    }
                    
                    # Determine hierarchy based on header level
                    if header_level == 1:
                        self.toc_entries.append(entry)
                        current_h1 = entry
                        current_h2 = None
                        current_h3 = None
                    elif header_level == 2:
                        entry['depth'] = 1
                        if current_h1:
                            current_h1['children'].append(entry)
                        else:
                            self.toc_entries.append(entry)
                        current_h2 = entry
                        current_h3 = None
                    elif header_level == 3:
                        entry['depth'] = 2
                        if current_h2:
                            current_h2['children'].append(entry)
                        elif current_h1:
                            current_h1['children'].append(entry)
                        else:
                            self.toc_entries.append(entry)
                        current_h3 = entry
                    else:  # h4
                        entry['depth'] = 3
                        if current_h3:
                            current_h3['children'].append(entry)
                        elif current_h2:
                            current_h2['children'].append(entry)
                        elif current_h1:
                            current_h1['children'].append(entry)
                        else:
                            self.toc_entries.append(entry)
            
            # Rough page estimation (will be refined after pagination)
            items_on_page += 1
            if items_on_page > 8:
                current_page += 1
                items_on_page = 0
    
    def _update_toc_page_indices(self):
        """Update TOC entries with actual page indices after pagination."""
        if not self.toc_entries or not self.pages:
            return
        
        # Build a map of header text to page index
        header_to_page = {}
        for page_idx, page_items in enumerate(self.pages):
            for item in page_items:
                if item['type'] == 'text' and item.get('is_header', False):
                    header_to_page[item['text']] = page_idx
        
        # Update TOC entries with correct page indices
        for entry in self.toc_entries:
            title = entry['title'].strip()
            if title in header_to_page:
                entry['page_index'] = header_to_page[title]


"""
Apple Books Clone - Book Card Component
Reusable book cover card with hover effects.
"""

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import io


class BookCard(ctk.CTkFrame):
    """A book cover card with Apple-style design."""
    
    def __init__(self, parent, book_data: dict, on_click=None, size="medium"):
        super().__init__(parent, fg_color="transparent")
        
        self.book_data = book_data
        self.on_click = on_click
        
        # Size configurations
        sizes = {
            "small": (100, 150),
            "medium": (140, 210),
            "large": (180, 270)
        }
        self.width, self.height = sizes.get(size, sizes["medium"])
        
        self._create_widgets()
        self._bind_events()
    
    def _create_widgets(self):
        """Create card widgets."""
        # Book cover container with shadow effect
        self.cover_frame = ctk.CTkFrame(
            self,
            width=self.width,
            height=self.height,
            corner_radius=8,
            fg_color=("#E8E8ED", "#2C2C2E"),
            border_width=1,
            border_color=("#D1D1D6", "#3A3A3C")
        )
        self.cover_frame.pack(pady=(0, 8))
        self.cover_frame.pack_propagate(False)
        
        # Cover image or placeholder
        if self.book_data.get("cover_image"):
            self._set_cover_image(self.book_data["cover_image"])
        else:
            self._create_placeholder_cover()
        
        # Book title
        title = self.book_data.get("title", "Unknown Title")
        if len(title) > 20:
            title = title[:18] + "..."
        
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7"),
            wraplength=self.width
        )
        self.title_label.pack(anchor="w")
        
        # Author
        author = self.book_data.get("author", "Unknown Author")
        if len(author) > 22:
            author = author[:20] + "..."
        
        self.author_label = ctk.CTkLabel(
            self,
            text=author,
            font=ctk.CTkFont(size=11),
            text_color=("#86868B", "#86868B")
        )
        self.author_label.pack(anchor="w")
        
        # Progress bar (if reading)
        progress = self.book_data.get("progress", 0)
        if progress > 0:
            self.progress_bar = ctk.CTkProgressBar(
                self,
                width=self.width,
                height=4,
                corner_radius=2,
                progress_color=("#007AFF", "#0A84FF")
            )
            self.progress_bar.pack(pady=(6, 0))
            self.progress_bar.set(progress / 100)
    
    def _set_cover_image(self, image_data: bytes):
        """Set cover image from bytes."""
        try:
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((self.width - 4, self.height - 4), Image.Resampling.LANCZOS)
            
            # Add rounded corners
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), image.size], radius=6, fill=255)
            
            image.putalpha(mask)
            
            self.cover_photo = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(self.width - 4, self.height - 4)
            )
            
            self.cover_label = ctk.CTkLabel(
                self.cover_frame,
                image=self.cover_photo,
                text=""
            )
            self.cover_label.pack(expand=True)
        except Exception:
            self._create_placeholder_cover()
    
    def _create_placeholder_cover(self):
        """Create a placeholder cover with gradient."""
        # Create gradient placeholder
        colors = [
            ("#FF6B6B", "#EE5A24"),
            ("#74B9FF", "#0984E3"),
            ("#55EFC4", "#00B894"),
            ("#FFEAA7", "#FDCB6E"),
            ("#DFE6E9", "#B2BEC3"),
            ("#A29BFE", "#6C5CE7"),
        ]
        
        # Pick color based on title hash
        title = self.book_data.get("title", "Book")
        color_idx = hash(title) % len(colors)
        start_color, end_color = colors[color_idx]
        
        # File type icon
        file_type = self.book_data.get("file_type", "epub").upper()
        icon = "📖" if file_type == "EPUB" else "📄"
        
        self.cover_label = ctk.CTkLabel(
            self.cover_frame,
            text=f"{icon}\n\n{file_type}",
            font=ctk.CTkFont(size=24),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        self.cover_label.pack(expand=True)
    
    def _bind_events(self):
        """Bind hover and click events to all widgets."""
        widgets = [self, self.cover_frame, self.title_label, self.author_label]
        
        # Add cover label if it exists
        if hasattr(self, 'cover_label'):
            widgets.append(self.cover_label)
        
        # Also bind to all children of cover_frame
        for child in self.cover_frame.winfo_children():
            if child not in widgets:
                widgets.append(child)
        
        for widget in widgets:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.cover_frame.configure(
            border_color=("#007AFF", "#0A84FF"),
            border_width=2
        )
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.cover_frame.configure(
            border_color=("#D1D1D6", "#3A3A3C"),
            border_width=1
        )
    
    def _on_click(self, event):
        """Handle click event."""
        if self.on_click:
            self.on_click(self.book_data)

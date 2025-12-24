"""
Apple Books Clone - Sidebar Component
Navigation sidebar with Apple-style design.
"""

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """Apple-style navigation sidebar."""
    
    def __init__(self, parent, on_navigate):
        super().__init__(parent, width=220, corner_radius=0)
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active_page = "home"
        
        # Configure colors
        self.configure(fg_color=("#F5F5F7", "#1C1C1E"))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create sidebar widgets."""
        # App title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(25, 30))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="📚 Books",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=("#1D1D1F", "#F5F5F7")
        )
        title_label.pack(anchor="w")
        
        # Navigation section
        nav_label = ctk.CTkLabel(
            self,
            text="Library",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#86868B", "#86868B")
        )
        nav_label.pack(anchor="w", padx=20, pady=(0, 8))
        
        # Navigation buttons
        nav_items = [
            ("home", "📖", "Reading Now"),
            ("library", "📚", "Library"),
            ("store", "🏪", "Book Store"),
        ]
        
        for page_id, icon, label in nav_items:
            self._create_nav_button(page_id, icon, label)
        
        # Separator
        separator = ctk.CTkFrame(self, height=1, fg_color=("#D1D1D6", "#3A3A3C"))
        separator.pack(fill="x", padx=20, pady=20)
        
        # Collections section
        collections_label = ctk.CTkLabel(
            self,
            text="Collections",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#86868B", "#86868B")
        )
        collections_label.pack(anchor="w", padx=20, pady=(0, 8))
        
        # Collection buttons
        collection_items = [
            ("favorites", "❤️", "Favorites"),
            ("want_to_read", "📌", "Want to Read"),
            ("finished", "✅", "Finished"),
        ]
        
        for page_id, icon, label in collection_items:
            self._create_nav_button(page_id, icon, label, is_collection=True)
        
        # Theme toggle at bottom
        self.pack_propagate(False)
        
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark Mode",
            font=ctk.CTkFont(size=13),
            command=self._toggle_theme,
            onvalue=1,
            offvalue=0
        )
        self.theme_switch.pack(anchor="w")
        
        # Set initial state
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()
    
    def _create_nav_button(self, page_id: str, icon: str, label: str, is_collection: bool = False):
        """Create a navigation button."""
        btn = ctk.CTkButton(
            self,
            text=f"  {icon}  {label}",
            font=ctk.CTkFont(size=14),
            anchor="w",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            text_color=("#1D1D1F", "#F5F5F7"),
            hover_color=("#E8E8ED", "#2C2C2E"),
            command=lambda: self._on_button_click(page_id)
        )
        btn.pack(fill="x", padx=12, pady=2)
        self.buttons[page_id] = btn
        
        # Set home as active by default
        if page_id == "home":
            self._set_active(page_id)
    
    def _on_button_click(self, page_id: str):
        """Handle navigation button click."""
        self._set_active(page_id)
        self.on_navigate(page_id)
    
    def _set_active(self, page_id: str):
        """Set the active navigation button."""
        # Reset all buttons
        for pid, btn in self.buttons.items():
            btn.configure(fg_color="transparent")
        
        # Highlight active button
        if page_id in self.buttons:
            self.buttons[page_id].configure(
                fg_color=("#007AFF", "#0A84FF")
            )
            self.active_page = page_id
    
    def _toggle_theme(self):
        """Toggle between light and dark mode."""
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

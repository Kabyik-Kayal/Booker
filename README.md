# 📚 Booker

A beautiful **Apple Books-inspired** e-book reader application built with Python and CustomTkinter. Manage your digital library, read EPUB and PDF files, and track your reading progress — all in a sleek, modern interface.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-1F6FEB?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Features

### 📖 E-Book Reader
- **EPUB & PDF Support** — Read your favorite books in both popular formats
- **Two-Page Spread Layout** — Enjoy an immersive reading experience
- **Progress Tracking** — Automatically saves your reading position
- **Smooth Navigation** — Page-by-page reading with optimized performance

### 📚 Library Management
- **Organized Collections** — Sort books into Favorites, Want to Read, Currently Reading, and Finished
- **Smart Search** — Quickly find books by title or author
- **Book Import** — Easily add new books to your library
- **Cover Display** — Beautiful book covers with metadata

### 🎨 Modern UI/UX
- **Apple Books-Inspired Design** — Clean, minimalist interface
- **Dark/Light Mode** — Automatic system theme detection
- **Responsive Layout** — Adapts to different window sizes
- **Sidebar Navigation** — Quick access to all sections

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Booker.git
   cd Booker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | ≥5.2.0 | Modern UI framework |
| [Pillow](https://python-pillow.org/) | ≥10.0.0 | Image processing |
| [EbookLib](https://github.com/aerkalov/ebooklib) | ≥0.18 | EPUB file handling |
| [PyMuPDF](https://pymupdf.readthedocs.io/) | ≥1.23.0 | PDF rendering |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | ≥4.12.0 | HTML/XML parsing |

---

## 📁 Project Structure

```
Booker/
├── main.py              # Application entry point
├── app.py               # Main application window & navigation
├── database.py          # SQLite database operations
├── requirements.txt     # Python dependencies
├── books.db             # SQLite database (auto-generated)
├── components/
│   ├── sidebar.py       # Navigation sidebar
│   └── book_card.py     # Book card component
└── pages/
    ├── home.py          # Home page with reading overview
    ├── library.py       # Library view with collections
    ├── store.py         # Book import functionality
    └── reader.py        # E-book reader interface
```

---

## 🎯 Usage

### Adding Books
1. Navigate to the **Store** page
2. Click **Import** to add EPUB or PDF files
3. Books are automatically added to your library

### Reading Books
1. Go to **Library** or **Home**
2. Click on any book cover to open the reader
3. Use arrow keys or click to navigate pages

### Managing Collections
- ❤️ **Favorites** — Mark books you love
- 📖 **Want to Read** — Queue up your reading list
- ✅ **Finished** — Track completed books

---

## 🛠️ Technical Details

- **Database**: SQLite with connection pooling for performance
- **Architecture**: Component-based UI with page navigation
- **Caching**: Implemented for images, fonts, and page content
- **Threading**: Background loading for smooth performance

---

## 📦 Building from Source

Build Booker as a standalone Windows executable (.exe) that can be installed and run like any desktop application.

### Prerequisites
- Python 3.8+
- All dependencies installed (`pip install -r requirements.txt`)

### Build Steps

1. **Run the build script**
   ```bash
   build.bat
   ```
   Or manually:
   ```bash
   pip install pyinstaller>=6.0.0
   pyinstaller booker.spec --clean
   ```

2. **Find your executable**
   ```
   dist/Booker/Booker.exe
   ```

3. **Distribute**
   - Zip the entire `dist/Booker/` folder for sharing
   - Or create an installer using [Inno Setup](https://jrsoftware.org/isinfo.php) or [NSIS](https://nsis.sourceforge.io/)

> **Note**: The `dist/Booker/` folder contains all required dependencies. Keep all files together when distributing.


---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by Apple Books
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Icons and design elements inspired by macOS

---

<p align="center">
  Made with ❤️
</p>

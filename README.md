# Daily Logbook

A simple cross-platform desktop app to track your daily activities.

## Features

- 📝 Log activities with optional descriptions
- 📅 Calendar to view previous days
- 📊 Activity stats (daily/weekly counts)
- 📋 Copy as formatted table (image or text)
- 💾 Export to CSV
- ✏️ Edit/delete activities
- 🖥️ Works on Windows, macOS, and Linux

## Quick Start

```bash
# Install dependencies
pip install tkcalendar pillow

# Windows only (for image clipboard)
pip install pywin32

# Run the app
python main.py
```

## Platform-Specific Notes

### Windows
No additional setup needed.

### macOS
Image clipboard works out of the box using built-in `osascript`.

### Linux
For "Copy as Image" feature, install one of these:
```bash
# Option 1: xclip (recommended)
sudo apt install xclip

# Option 2: xsel (alternative)
sudo apt install xsel
```

## Customization

The export appearance can be customized via **Options > Export Settings**:

- **Font Sizes** - Title, header, body, and summary text sizes
- **Column Widths** - Adjust width of each column (Proyecto/Area, Avance, Impacto, Estado)
- **Spacing** - Cell padding and row height settings

Changes are previewed in real-time and saved automatically.

## Build Executable

```bash
pip install pyinstaller
python -m PyInstaller "Daily Logbook.spec"
```

Your .exe will be in the `dist/` folder.

## Data Storage

Activities are saved locally in `~/.logbook/` as JSON files (one file per day).
Settings are persisted to `~/.logbook/image_settings.json`.

## Project Structure

The application uses a modular design with separated concerns:

- **gui.py** - Main application UI and orchestration
- **settings_manager.py** - Manages export settings persistence
- **image_exporter.py** - Handles image generation and clipboard operations
- **text_wrapper.py** - Text wrapping utilities (UI and image rendering)
- **dialog_manager.py** - Manages settings dialog and export preview
- **storage.py** - Data persistence layer for activities
- **main.py** - Entry point

## Requirements

- Python 3.6+
- tkinter (included with Python)
- tkcalendar
- Pillow
- pywin32 (Windows only)

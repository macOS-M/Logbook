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

## Build Executable

```bash
pip install pyinstaller
python -m PyInstaller "Daily Logbook.spec"
```

Your .exe will be in the `dist/` folder.

## Data Storage

Activities are saved locally in `~/.logbook/` as JSON files (one file per day).

## Requirements

- Python 3.6+
- tkinter (included with Python)
- tkcalendar
- Pillow
- pywin32 (Windows only)

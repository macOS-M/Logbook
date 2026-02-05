# How to Create an .exe for Daily Logbook

## Using PyInstaller

PyInstaller is the easiest way to convert your Python application to a standalone .exe file.

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Create the .exe

Run this command from the project directory (where `main.py` is located):

```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data ".:." main.py
```

**Options explained:**
- `--onefile` - Creates a single .exe file instead of a folder
- `--windowed` - Removes the console window (cleaner look)
- `--icon=icon.ico` - Sets the .exe icon (optional, remove if no icon file)
- `--add-data ".:."` - Includes all data files needed

### Step 3: Find Your .exe

The executable will be in:
```
dist/main.exe
```

Copy this file wherever you need it!

## Option A: Using the Build Script (Recommended)

Create a `build.bat` file in your project directory:

```batch
@echo off
echo Building Daily Logbook...
pyinstaller --onefile --windowed --name "Daily Logbook" main.py
echo.
echo Build complete! Your executable is in the 'dist' folder.
pause
```

Then just double-click `build.bat` to create the .exe.

## Option B: Creating with Custom Icon

If you want a custom icon:

1. Create or get a `.ico` file (convert PNG to ICO online if needed)
2. Place it in your project directory as `icon.ico`
3. Run:

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name "Daily Logbook" main.py
```

## Option C: Creating an Installer (Advanced)

For a professional installer (.msi), use NSIS:

1. Install NSIS: https://nsis.sourceforge.io/
2. Create a setup script (ask if you want help with this)
3. Use NSIS to build the installer

## Common Issues & Solutions

### Issue: tkcalendar not included
**Solution:** Explicitly add it:
```bash
pyinstaller --onefile --windowed --hidden-import=tkcalendar main.py
```

### Issue: "This app can't run on your PC"
**Solution:** Run on the same Windows version you're targeting, or use a VM

### Issue: File size too large
**Solution:** Use UPX compression (advanced):
```bash
pyinstaller --onefile --windowed --upx-dir=path/to/upx main.py
```

## Quick Command (Copy & Paste)

This command works for your project:

```bash
pyinstaller --onefile --windowed --name "Daily Logbook" --hidden-import=tkcalendar main.py
```

Then find your .exe in the `dist/` folder!

## Distribution

Once you have the .exe:
- You can share it directly with others
- They can run it without having Python installed
- They just need Windows

---

## One-Command Solution

If you just want to build quickly:

1. Open PowerShell in your project folder
2. Install PyInstaller if you haven't: `pip install pyinstaller`
3. Run: `pyinstaller --onefile --windowed --name "Daily Logbook" --hidden-import=tkcalendar main.py`
4. Get your .exe from the `dist` folder

That's it!
#RUN
python -m PyInstaller --onefile --windowed --name "Daily Logbook" --hidden-import=tkcalendar main.py
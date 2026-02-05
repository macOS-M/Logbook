"""Main entry point for Daily Logbook application"""

import tkinter as tk
from storage import DataStorage
from gui import DailyLogbookUI


def main():
    """Initialize and run the application"""
    root = tk.Tk()
    storage = DataStorage()
    app = DailyLogbookUI(root, storage)
    root.mainloop()


if __name__ == "__main__":
    main()

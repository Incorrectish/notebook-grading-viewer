import tkinter as tk
from tkinter import PhotoImage, Text
import nbformat
import re
from PIL import Image, ImageTk

def load_cells_from_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    return nb['cells']

def insert_image(text_widget, img_path):
    try:
        # Open the image file with PIL
        img = Image.open(img_path)
        # Resize the image to fit better within the text area
        img = img.resize((300, 200)) #, Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)

        # Insert the image into the text widget
        text_widget.image_create(tk.END, image=photo)
        text_widget.image_cache.append(photo)  # Keep a reference!
        text_widget.insert(tk.END, '\n')  # Add a newline after the image
    except Exception as e:
        print(f"Error loading image {img_path}: {e}")

def create_gui_with_notebook_cells(cells):
    root = tk.Tk()
    root.title("Notebook Viewer")

    text_area = Text(root, wrap=tk.WORD, width=100, height=40)
    text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    text_area.image_cache = []  # To prevent images from being garbage collected

    for cell in cells:
        if cell.cell_type == 'code':
            text_area.insert(tk.END, f"# Code Cell:\n{cell.source}\n\n")
        elif cell.cell_type == 'markdown':
            # Insert text and look for image patterns
            text_area.insert(tk.END, f"# Markdown Cell:\n")
            lines = cell.source.split('\n')
            for line in lines:
                # Simple pattern to find Markdown image syntax ![alt text](path)
                match = re.search(r'!\[.*?\]\((.*?)\)', line)
                if match:
                    image_path = match.group(1)
                    insert_image(text_area, image_path)
                else:
                    text_area.insert(tk.END, line + '\n')

    root.mainloop()

# Example usage
notebook_path = 'CMSC320_RegressionGradientDescentNeuralNetworks_11865414_Lee.ipynb'
cells = load_cells_from_notebook(notebook_path)
create_gui_with_notebook_cells(cells)

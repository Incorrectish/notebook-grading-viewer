import nbformat
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os

# random hash for my name + "single" to ensure none of the gradescope downloaded
# notebooks contains this string. You will see why this is important later :)
UNIQUE_FILE_EXTENDER = '_single_cb39cf67e1fdf2d08a1e31fa30a555bdfe4d062c'

""" We need to strip the cell of its leading "#"s or " "s because every cell
 begins with something like:
 
# # # STUDENT INPUT # # #

or 


##### 1.1. Preparation of Training and Testing Set

"""
def remove_leading_hashes_and_spaces(text: str) -> str:
    text = text.lstrip()
    while text and (text[0] == '#' or text[0] == ' '):
        text = text[1:].lstrip()
    return text

# Process the notebook content as needed


# To find eg 3.1, we look for either a cell that starts with 3.1 or we look for
# if we have passed section 3 BUT NOT section 4 and then look for part 1


# thoughts: first run setup, where you can specify the problem then the
# directory. Specify also how many followup cells you need

# collect our cells: write them to a notebook. Convert that notebook to HTML.
# Display the HTML notebook. Save the state of the directory into a list. Once
# that directory has a new file added, remove the files created and repeat with
# the new one


def main():
    student_notebook_path = 'CMSC320_RegressionGradientDescentNeuralNetworks_11865414_Lee.ipynb'
    notebook_base_name, _ = os.path.splitext(student_notebook_path)
    with open(student_notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)

# Access notebook content
    cells = notebook['cells']

    keyword = '1.1'  # Define your keyword here
    cells_with_keyword = []
    followup_cells = 1

    for i, cell in enumerate(cells):
        # if cell.cell_type == 'code':  # or 'markdown' if you are interested in markdown cells
            # Checking if the cell content starts with the keyword
        stripped_leading_source = remove_leading_hashes_and_spaces(cell.source)
        if stripped_leading_source.startswith(keyword):
            # we are assuming there is a output cell after this, we could do error
            # checking here instead, but not yet
            # text cell, code cell, output cell
            cells_with_keyword.append(cells[i:i+followup_cells+1])
            break

    if len(cells_with_keyword) == 0:
        pass


    # Create a new notebook
    nb = notebook

    # Assign your list of cells to the notebook
    nb['cells'] = cells_with_keyword[0]

    # Path to the new notebook file
    notebook_path = notebook_base_name + '.ipynb'

    # Write the notebook to the file
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

    print(f"Notebook saved to {notebook_path}")

    os.system(f'.venv/bin/jupyter nbconvert --to html --template classic {notebook_path}')

    # Get the current working directory
    current_directory = os.getcwd()

    print(current_directory)

    app = QApplication(sys.argv)

    browser = QWebEngineView()
    browser.load(QUrl(f"file:///{current_directory}/{notebook_base_name}_single.html"))
    browser.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

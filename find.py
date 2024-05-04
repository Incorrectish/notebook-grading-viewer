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


def main(keyword: str):
    student_notebook_path = 'CMSC320_RegressionGradientDescentNeuralNetworks_11865414_Lee.ipynb'
    notebook_base_name, _ = os.path.splitext(student_notebook_path)
    with open(student_notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)

# Access notebook content
    cells = notebook['cells']

    # if i split "1" by ".", I get ["1"]
    parts = keyword.strip().split('.')
    section_number = int(parts[0].strip()) - 1
    print(section_number)
    if len(parts) == 1:
        part = None
    else:
        part = parts[1]
    # numbers are weird, like 1.2 is actually 2.2 for some reason, so I'll just
    # increment section when searching

    cells_with_keyword = []
    followup_cells = 1

    # for cell in cells:
    #     print(cell.source)
    #     print("----------------------------------------")
    #
    # return

    if part != None:
        for i, cell in enumerate(cells):
            # if cell.cell_type == 'code':  # or 'markdown' if you are interested in markdown cells
                # Checking if the cell content starts with the keyword
            stripped_leading_source = remove_leading_hashes_and_spaces(cell.source)
            if stripped_leading_source.startswith(f"{section_number}.{part}"):
                # we are assuming there is a output cell after this, we could do error
                # checking here instead, but not yet
                # text cell, code cell, output cell
                cells_with_keyword.append(cells[i:i+followup_cells+1])
                break

    if len(cells_with_keyword) == 0:
        section= False 
        for i, cell in enumerate(cells):
            stripped_leading_source = remove_leading_hashes_and_spaces(cell.source)
            if stripped_leading_source.startswith(f"Section {section_number}"):
                section = True
            elif section_number == 4 and stripped_leading_source.startswith("Final Section"):
                cells_with_keyword.append(cells[i:i+followup_cells+1])
                break
            elif section_number == 5 and stripped_leading_source.startswith("Bonus Question"):
                cells_with_keyword.append(cells[i:i+followup_cells+1])
                break
            elif stripped_leading_source.startswith(f"Part {part}") and section:
                cells_with_keyword.append(cells[i:i+followup_cells+1])
                break
                
        

    # Create a new notebook
    nb = notebook

    # Assign your list of cells to the notebook
    nb['cells'] = cells_with_keyword[0]

    # Path to the new notebook file
    notebook_path = notebook_base_name + '_single' + '.ipynb'

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
    # questions = ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "3.1", "3.2",
    #              "3.3", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "5", "6"]
    # for question in questions:
    # Usage: provide the question in the format on gradescope, eg if you want
    # 1.1 provide 2.1 for the question. 4.1 for 3.1 etc. 
    # Followup cells is the number of cells you want to see after the question
    # cell. 
    # .venv/bin/python3 update_loop.py <question> <follow_up_cells>
    main(sys.argv[1])

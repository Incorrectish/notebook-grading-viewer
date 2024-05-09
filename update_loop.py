import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
import nbformat
import queue
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

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

# When you download a file, it takes time to fully write the contents of the
# file, and the file will appear empty until it has finished downloading. So we
# just keep trying to read the file until it has finished downloading. We cap
# the max attempts in order to ensure that we don't loop forever
def read_notebook_with_retries(filepath, max_attempts=25, retry_delay=1):
    """Attempt to read a Jupyter notebook file with retries on failure."""
    attempts = 0
    while attempts < max_attempts:
        try:
            with open(filepath, 'r') as f:
                return nbformat.read(f, as_version=4)
        except (IOError, nbformat.reader.NotJSONError) as e:
            print(f"Error reading file {filepath}: {e}, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            attempts += 1
    raise Exception(f"Failed to read notebook after {max_attempts} attempts.")

# Search engine for question. Given question finds the cells corressponding to
# the question and the next followup_cells cells. This is the function that
# probably should be adapted in case you want to generalize this program to work
# with more than just CMSC320 homework 5 :)
def search(cells, question, followup_cells):
    parts = question.strip().split('.')
    # numbers are weird, like 1.2 is actually 2.2 for some reason, so I'll just
    # increment section when searching
    section_number = int(parts[0].strip()) - 1
    print(section_number)
    if len(parts) == 1:
        part = None
    else:
        part = parts[1]

    cells_with_keyword = None

    if part != None:
        for i, cell in enumerate(cells):
            # if cell.cell_type == 'code':  # or 'markdown' if you are interested in markdown cells
                # Checking if the cell content starts with the keyword
            stripped_leading_source = remove_leading_hashes_and_spaces(cell.source)
            if stripped_leading_source.startswith(f"{section_number}.{part}"):
                # we are assuming there is a output cell after this, we could do error
                # checking here instead, but not yet
                # text cell, code cell, output cell
                cells_with_keyword = cells[i:i+followup_cells+1]
                break

    if cells_with_keyword == None:
        section= False 
        for i, cell in enumerate(cells):
            stripped_leading_source = remove_leading_hashes_and_spaces(cell.source)
            if stripped_leading_source.startswith(f"Section {section_number}"):
                section = True
            elif section_number == 4 and stripped_leading_source.startswith("Final Section"):
                cells_with_keyword = cells[i:i+followup_cells+1]
                break
            elif section_number == 5 and stripped_leading_source.startswith("Bonus Question"):
                cells_with_keyword = cells[i:i+followup_cells+1]
                break
            elif stripped_leading_source.startswith(f"Part {part}") and section:
                cells_with_keyword = cells[i:i+followup_cells+1]
                break
    return cells_with_keyword

# We read the notebook, search for the specified question, and get the cell that contains the
# question along with the next <followup_cells> cells. We write that to a new
# notebook, convert that notebook to HTML, then put it in our rendering queue
def process_notebook(student_notebook_path, html_queue, question, followup_cells):
    notebook_base_name, _ = os.path.splitext(student_notebook_path)
    notebook = read_notebook_with_retries(student_notebook_path)

    cells = notebook['cells']

    # if i split "1" by ".", I get ["1"]

    cells_with_keyword = search(cells, question, followup_cells)

    nb = notebook
    nb['cells'] = cells_with_keyword
    single_notebook_path = notebook_base_name + UNIQUE_FILE_EXTENDER + '.ipynb'
    with open(single_notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print(f"Notebook saved to {single_notebook_path}")

    single_html_path = notebook_base_name + UNIQUE_FILE_EXTENDER + '.html'
    os.system(f'.venv/bin/jupyter nbconvert --to html --template classic --output {single_html_path} {single_notebook_path}')
    html_full_path = os.path.join(os.getcwd(), single_html_path)
    html_queue.put(html_full_path)

# Basic class for our HTML renderer
class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        self.showMaximized()

    def load_url(self, url):
        self.browser.setUrl(QUrl(url))

# Create our HTML renderer and then run our event handlerer. We check the
# directory to see if any new ".ipynb" files appear. If they do run the process
# function and add them to our rendering queue to render. 
def main(keyword: str, followup_cells: int, path):
    app = QApplication(sys.argv)
    window = BrowserWindow()

    html_queue = queue.Queue()

    event_handler = MyHandler(html_queue, keyword, followup_cells)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            print(os.listdir(path))
            if not html_queue.empty():
                url = html_queue.get()
                window.load_url(f"file:///{url}")
                print(os.listdir(path))
            app.processEvents()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

class MyHandler(FileSystemEventHandler):
    def __init__(self, html_queue, keyword, followup_cells):
        super().__init__()
        self.keyword = keyword
        self.html_queue = html_queue
        self.followup_cells = followup_cells

    # we only want to process new downloaded notebooks, not the intermediary
    # notebooks that this program creates, so I added the uniuqe file extender
    # to identify the intermediary files we create and not trigger on them
    def process(self, event):
        if event.src_path.endswith('.ipynb') and not (UNIQUE_FILE_EXTENDER in event.src_path):
            print(f"Detected new notebook: {event.src_path}")
            process_notebook(event.src_path, self.html_queue, self.keyword,
                             self.followup_cells)

    def on_created(self, event):
        self.process(event)

if __name__ == "__main__":
    # Usage:
    # provide the question in the format on gradescope, eg if you want
    # 1.1 provide 2.1 for the question. 4.1 for 3.1 etc. 
    # Followup cells is the number of cells you want to see after the question
    # cell. 
    # wait time is the time you want the application to wait before processing
    # the notebook. It's needed because downloads aren't instant, and if you try
    # to read the notebook before the download finished, you will get an error
    # .venv/bin/python3 update_loop.py <question> <follow_up_cells> 
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("""Error: please provide arguments in the following format:\n
            .venv/bin/python3 update_loop.py <question> <follow_up_cells> <dir>
            where:

            question is the question in the format on gradescope, eg if you want
            1.1 provide 2.1 for the question. 4.1 for 3.1 etc. 
            followup cells is the number of cells you want to see after the question
            cell. 

            dir is the directory where your .ipynbs can be found. Note, this
            directory will be polluted with new .ipynb files and html files, so
            choose a directory where that is fine with you. this argument is
            optional however, and if you don't provide it, it will default to
            the directory this script is in
            """)
    else: 
        main(sys.argv[1], int(sys.argv[2]), ('.' if len(sys.argv) == 3 else
            sys.argv[3]))

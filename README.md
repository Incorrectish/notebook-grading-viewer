# Explanation

This program is intended to be used in the following way. You run the program
and provide a directory where you will download your .ipynb files and the
problem that you are trying to grade. Then it will display that problem. When
you want to go to the next person to grade, you simply download the next
person's notebook and it will automatically update to find the problem from the
next person and re render. 
You use it in the following way: 


# Usage

```.venv/bin/python3 update_loop.py <question> <follow_up_cells> <dir>```
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

# Installation instructions with script
A prerequisite to both of these is that you have both git and python3 installed.
run the following commands

```
git clone https://github.com/Incorrectish/notebook-grading-viewer.git
cd notebook-grading-viewer
chmod +x install.sh
./install.sh
```

# Installation instructions detailed
In case my install script doesn't work, here is what you need to do. In the
notebook-grading-viewer directory, you need to create a virtual environment called ".venv". 

```
git clone https://github.com/Incorrectish/notebook-grading-viewer.git
cd notebook-grading-viewer
```

```python3 -m venv.venv```

Then you need to install the following dependencies:

```
.venv/bin/pip3 install jupyter 
.venv/bin/pip3 install nbconvert
.venv/bin/pip3 install watchdog 
.venv/bin/pip3 install PyQTWebEngine
.venv/bin/pip3 install PyQT5
```

# Known things to not do 
Don't download the same file twice into the tracked directory. This causes a
crash. I could spend time debugging this, but this is an easy thing for you guys
to not do :)

By this I mean you shouldn't have a directory that's being tracked that has a
file like: "123.ipynb", and then you download "123(1).ipynb"

This might become a problem if you want to grade a second problem and redownload. For this I reccomend purging the directory of all the ".ipynb"s and ".htmls" by running(IN THAT DIRECTORY ONLY)
```
rm *.ipynb
rm *.html
```

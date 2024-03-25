# Exlogs

 ##  Introduction
This is a simple keyword-based decompress extract files project written in Python. This project helps classify logs stolen using Redline Stealer malware and compressed files downloaded from hacking groups(Cloud_Mix, Logs_Mix, Combos) We support to decompress only the parts you want, and sort the Password.txt files.

# Getting Started  
Below are the Instructions on setting up the project Locally.</br>
## Prequisites 
Below are the Things you will need to use the software and How to install them :
- Operating System - Ubuntu
- Python 3.9.x - 3.10.x ( 3.10.12 Tested )
- Pip 3 (Usually gets Installed with Python)

if all the above prequisities are Satisfied, you may proceedto the next section.

## Installation
Follow these instructions to Setup your Own instance of the App :

</br>


### 1 : Clone the Repo 
```bash
git clone https://github.com/wogho/Exlogs.git
```
### 2 : Cd to the folder
```bash
cd Exlogs
```
### 3 : Install the PIP packages/dependencies
```bash
pip3 install -r ttkbootstrap

```

</br>

### 4 : It's done 🎉 | Run the app
```bash
  python3 gui.py
```
</br>
And Congrats 🎉 the Application would start if you have followed each step correctly.
</br>

# Info
The code provided is a Python script that creates a GUI application using the Tkinter library. Here's a summary of what each tab does:
### Setting Tab (tab1):

Allows the user to extract files from RAR and ZIP archives based on selected keywords.
Provides options to add keywords, select compression formats (RAR, ZIP, or both), and initiate the extraction process.
Includes utility functions such as deleting empty folders, deleting all RAR and ZIP files, and moving files to a new directory based on the current date.

### Filter Tab (tab2):

Provides a list of default sites for filtering data.
Allows users to add new sites to the list.
Includes a button to classify data based on the selected sites. The data is extracted from password files (Passwords.txt or All Passwords.txt) and saved to separate text files for each site.

### File Tab (tab3):

Implements a file search engine that allows users to search for files within a specified directory based on search terms (contains, starts with, or ends with).
Displays search results in a TreeView widget, showing file names, modification dates, types, sizes, and paths.

### View Tab (tab4):

Includes a text reader that allows users to browse and open text files.
Displays the content of the selected text file in a ScrolledText widget.
Overall, this application provides a variety of file management and data filtering functionalities through a user-friendly graphical interface.


# Todo Update

- [ ] Displays decompression progress
- [x] txt file classification "filter" function
- [ ] Log list showing recently unzipped file name and date/time

# License

Distributed under the Apache License 2.0. See [`LICENSE.txt`](/LICENSE) for more information.

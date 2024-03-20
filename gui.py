import os
import datetime
import subprocess
import shutil
import logging
import pathlib
import queue
import tkinter as tk
import ttkbootstrap as ttk
import tkinter.messagebox as messagebox
from datetime import datetime
from queue import Queue
from threading import Thread
from tkinter.filedialog import askdirectory
from tkinter import *
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from ttkbootstrap import utility
from ttkbootstrap.widgets import Floodgauge
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText

current_process = None  # 현재 실행 중인 프로세스를 추적하기 위한 변수
DEFAULT_KEYWORDS = ["KR*", "[KR]*", "*[KR]*"]

def add_keyword():
    keyword = keyword_entry.get().strip()
    if keyword:
        keyword_listbox.insert(tk.END, keyword)
        keyword_entry.delete(0, tk.END)

def refresh_listbox():
    keyword_listbox.delete(0, tk.END)
    for keyword in keywords_list:
        keyword_listbox.insert(tk.END, keyword)

##### tab1
def extract_files():
    global current_process
    rar_selected = rar_var.get()  # RAR 체크박스의 상태 확인
    zip_selected = zip_var.get()  # ZIP 체크박스의 상태 확인
    all_selected = all_var.get()  # All 체크박스의 상태 확인
    
    # 모든 파일 형식이 선택되지 않은 경우
    if not rar_selected and not zip_selected and not all_selected:
        print("압축 파일을 선택하세요.")
        return
    
    for file in os.listdir('.'):
        if rar_selected or all_selected and (file.endswith('.rar') or file.endswith('.RAR')):
            selected_keywords = keyword_listbox.curselection()
            keywords = [keyword_listbox.get(idx) for idx in selected_keywords]
            # 사용자가 선택한 키워드를 적절한 형식으로 조합하여 압축 해제 명령어를 생성
            keyword_string = ' '.join([f"'{keyword}'" for keyword in keywords])
            rar_command = f"mkdir '{file[:-4]}' && 7z x '{file}' -o'{file[:-4]}' -r {keyword_string}" #432code
            try:
                current_process = subprocess.Popen(rar_command, shell=True)
                current_process.communicate()  # 프로세스가 완료될 때까지 대기
                print(f"{file} 압축 해제 완료")
                messagebox.showinfo('압축 해제 완료', '압축 해제가 완료되었습니다.')
            except subprocess.CalledProcessError as e:
                print(f"{file} 압축 해제 중 오류 발생:", e)
        if zip_selected or all_selected and (file.endswith('.zip') or file.endswith('.ZIP')):
            selected_keywords = keyword_listbox.curselection()
            keywords = [keyword_listbox.get(idx) for idx in selected_keywords]
            # 사용자가 선택한 키워드를 적절한 형식으로 조합하여 압축 해제 명령어를 생성
            keyword_string = ' '.join([f"'{keyword}'" for keyword in keywords])
            zip_command = f"mkdir '{file[:-4]}' && 7z x '{file}' -o'{file[:-4]}' -r {keyword_string}"
            try:
                current_process = subprocess.Popen(zip_command, shell=True)
                current_process.communicate()  # 프로세스가 완료될 때까지 대기
                print(f"{file} 압축 해제 완료")
                messagebox.showinfo('압축 해제 완료', '압축 해제가 완료되었습니다.')
            except subprocess.CalledProcessError as e:
                print(f"{file} 압축 해제 중 오류 발생:", e)

def cancel_extraction():
    global current_process
    if current_process:
        current_process.terminate()
        print("압축 해제 작업이 취소되었습니다.")
    else:
        print("현재 실행 중인 압축 해제 작업이 없습니다.")

def delete_empty_folders():
    # 빈 파일 삭제 명령어
    delete_command = r"find . -maxdepth 1 -mindepth 1 -type d -empty -exec rmdir '{}' \; -exec echo '비어 있는 디렉터리 삭제 완료: {}' \;"

    # 명령어 실행
    try:
        subprocess.run(delete_command, shell=True, check=True)
        print("빈 파일 삭제 완료")
    except subprocess.CalledProcessError as e:
        print("빈 파일 삭제 중 오류 발생:", e)

def delete_all_rar():
    # 모든 RAR 삭제 명령어
    delete_rar_command = r"find . -type f \( -name '*.RAR' -o -name '*.rar' -o -name '*.ZIP' -o -name '*.zip' \) -exec rm -rf {} \; && echo 'rar empty done'"

    # 명령어 실행
    try:
        subprocess.run(delete_rar_command, shell=True, check=True)
        print("모든 RAR 삭제 완료")
    except subprocess.CalledProcessError as e:
        print("모든 RAR 삭제 중 오류 발생:", e)

def move_files_to_new_directory():
    # Create a new directory with the current date
    today_date = datetime.now().strftime("%Y%m%d")
    new_directory_path = f"./{today_date}"
    
    try:
        os.makedirs(new_directory_path)
        print(f"새 디렉토리 생성: {new_directory_path}")
    except FileExistsError:
        print(f"디렉토리 이미 존재: {new_directory_path}")

    # Move all files (except .py files and the assets directory) to the new directory
    for file_name in os.listdir('.'):
        if file_name.endswith('.py') or file_name.endswith('.ipynb_checkpoints') or file_name == 'assets':
            continue

        source_path = os.path.join('.', file_name)
        destination_path = os.path.join(new_directory_path, file_name)
        
        try:
            shutil.move(source_path, destination_path)
            print(f"{file_name}을(를) {new_directory_path}로 이동 완료")
        except Exception as e:
            print(f"{file_name} 이동 중 오류 발생:", e)


##### tab3 
class FileSearchEngine(ttk.Frame):

    queue = queue.Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        # application variables
        _path = pathlib.Path().absolute().as_posix()
        self.path_var = StringVar(value=_path)
        self.term_var = StringVar(value='md')
        self.type_var = StringVar(value='endswith')

        # header and labelframe option container
        option_text = "Complete the form to begin your search"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_path_row()
        self.create_term_row()
        self.create_type_row()
        self.create_results_view()

        self.progressbar = ttk.Progressbar(
            master=self, 
            mode="indeterminate", 
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack(fill=X, expand=YES)

    def create_path_row(self):
        """Add path row to labelframe"""
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Path", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row, 
            text="Browse", 
            command=self.on_browse, 
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_term_row(self):
        """Add term row to labelframe"""
        term_row = ttk.Frame(self.option_lf)
        term_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(term_row, text="Term", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(term_row, textvariable=self.term_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        search_btn = ttk.Button(
            master=term_row, 
            text="Search", 
            command=self.on_search, 
            bootstyle=OUTLINE, 
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)

    def create_type_row(self):
        """Add type row to labelframe"""
        type_row = ttk.Frame(self.option_lf)
        type_row.pack(fill=X, expand=YES)
        type_lbl = ttk.Label(type_row, text="Type", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        contains_opt = ttk.Radiobutton(
            master=type_row, 
            text="Contains", 
            variable=self.type_var, 
            value="contains"
        )
        contains_opt.pack(side=LEFT)

        startswith_opt = ttk.Radiobutton(
            master=type_row, 
            text="StartsWith", 
            variable=self.type_var, 
            value="startswith"
        )
        startswith_opt.pack(side=LEFT, padx=15)

        endswith_opt = ttk.Radiobutton(
            master=type_row, 
            text="EndsWith", 
            variable=self.type_var, 
            value="endswith"
        )
        endswith_opt.pack(side=LEFT)
        endswith_opt.invoke()

    def create_results_view(self):
        """Add result treeview to labelframe"""
        self.resultview = ttk.Treeview(
            master=self, 
            bootstyle=INFO, 
            columns=[0, 1, 2, 3, 4],
            show=HEADINGS
        )
        self.resultview.pack(fill=BOTH, expand=YES, pady=10)

        # setup columns and use `scale_size` to adjust for resolution
        self.resultview.heading(0, text='Name', anchor=W)
        self.resultview.heading(1, text='Modified', anchor=W)
        self.resultview.heading(2, text='Type', anchor=E)
        self.resultview.heading(3, text='Size', anchor=E)
        self.resultview.heading(4, text='Path', anchor=W)
        self.resultview.column(
            column=0, 
            anchor=W, 
            width=125, 
            stretch=False
        )
        self.resultview.column(
            column=1, 
            anchor=W, 
            width=140, 
            stretch=False
        )
        self.resultview.column(
            column=2, 
            anchor=E, 
            width=50, 
            stretch=False
        )
        self.resultview.column(
            column=3, 
            anchor=E, 
            width=50, 
            stretch=False
        )
        self.resultview.column(
            column=4, 
            anchor=W, 
            width=300
        )

    def on_browse(self):
        """Callback for directory browse"""
        path = askdirectory(title="Browse directory")
        if path:
            self.path_var.set(path)

    def on_search(self):
        """Search for a term based on the search type"""
        search_term = self.term_var.get()
        search_path = self.path_var.get()
        search_type = self.type_var.get()

        if search_term == '':
            return

        # start search in another thread to prevent UI from locking
        Thread(
            target=self.file_search, 
            args=(search_term, search_path, search_type), 
            daemon=True
        ).start()
        self.progressbar.start(10)

        iid = self.resultview.insert(
            parent='', 
            index=END, 
        )
        self.resultview.item(iid, open=True)
        self.after(100, lambda: self.check_queue(iid))

    def check_queue(self, iid):
        """Check file queue and print results if not empty"""
        if all([
            self.searching, 
            not self.queue.empty()
        ]):
            filename = self.queue.get()
            self.insert_row(filename, iid)
            self.update_idletasks()
            self.after(100, lambda: self.check_queue(iid))
        elif all([
            not self.searching,
            not self.queue.empty()
        ]):
            while not self.queue.empty():
                filename = self.queue.get()
                self.insert_row(filename, iid)
            self.update_idletasks()
            self.progressbar.stop()
        elif all([
            self.searching,
            self.queue.empty()
        ]):
            self.after(100, lambda: self.check_queue(iid))
        else:
            self.progressbar.stop()

    def insert_row(self, file, iid):
        """Insert new row in tree search results"""
        try:
            _stats = file.stat()
            _name = file.stem
            _timestamp = datetime.fromtimestamp(_stats.st_mtime)
            _modified = _timestamp.strftime(r'%m/%d/%Y %I:%M:%S%p')
            _type = file.suffix.lower()
            _size = self.convert_size(_stats.st_size)
            _path = file.as_posix()
            iid = self.resultview.insert(
                parent='', 
                index=END, 
                values=(_name, _modified, _type, _size, _path)
            )
            self.resultview.selection_set(iid)
            self.resultview.see(iid)
        except OSError:
            return

    @staticmethod
    def file_search(term, search_path, search_type):
        """Recursively search directory for matching files"""
        FileSearchEngine.searching = True
        if search_type == 'contains':
            FileSearchEngine.find_contains(term, search_path)
        elif search_type == 'startswith':
            FileSearchEngine.find_startswith(term, search_path)
        elif search_type == 'endswith':
            FileSearchEngine.find_endswith(term, search_path)

    @staticmethod
    def find_contains(term, search_path):
        """Find all files that contain the search term"""
        for path, _, files in os.walk(search_path):
            if files:
                for file in files:
                    if term in file:
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.searching = False

    @staticmethod
    def find_startswith(term, search_path):
        """Find all files that start with the search term"""
        for path, _, files in os.walk(search_path):
            if files:
                for file in files:
                    if file.startswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.searching = False

    @staticmethod
    def find_endswith(term, search_path):
        """Find all files that end with the search term"""
        for path, _, files in os.walk(search_path):
            if files:
                for file in files:
                    if file.endswith(term):
                        record = pathlib.Path(path) / file
                        FileSearchEngine.queue.put(record)
        FileSearchEngine.searching = False

    @staticmethod
    def convert_size(size):
        """Convert bytes to mb or kb depending on scale"""
        kb = size // 1000
        mb = round(kb / 1000, 1)
        if kb > 1000:
            return f'{mb:,.1f} MB'
        else:
            return f'{kb:,d} KB'      

##### tab4
class TextReader(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.filename = ttk.StringVar()
        self.pack(fill=BOTH, expand=YES)
        self.create_widget_elements()

    def create_widget_elements(self):
        """Create and add the widget elements"""
        style = ttk.Style()
        self.textbox = ScrolledText(
            master=self,
            highlightcolor=style.colors.primary,
            highlightbackground=style.colors.border,
            highlightthickness=1
        )
        self.textbox.pack(fill=BOTH)
        default_txt = "Click the browse button to open a new text file."
        self.textbox.insert(END, default_txt)

        file_entry = ttk.Entry(self, textvariable=self.filename)
        file_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5), pady=10)

        browse_btn = ttk.Button(self, text="Browse", command=self.open_file)
        browse_btn.pack(side=RIGHT, fill=X, padx=(5, 0), pady=10)

    def open_file(self):
        path = askopenfilename()
        if not path:
            return

        with open(path, encoding='utf-8') as f:
            self.textbox.delete('1.0', END)
            self.textbox.insert(END, f.read())
            self.filename.set(path)


root = ttk.Window(themename='vapor')
root.title("Exlogs")

keywords_list = DEFAULT_KEYWORDS.copy()

# 탭 추가
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)

tab_control.add(tab1, text='Setting')
tab_control.add(tab2, text='Filter')
tab_control.add(tab3, text='File')
tab_control.add(tab4, text='View')
tab_control.pack(expand=True, fill=tk.BOTH)

FileSearchEngine(tab3)
TextReader(tab4)

# 탭1 항목

### extract 프레임 
extract_frame = LabelFrame(tab1, text='Extract')  # 탭1에 프레임 추가
extract_frame.pack(side=tk.LEFT, padx=20, pady=20, fill='both', expand=True)  # 프레임 외부여백

extract_label = ttk.Label(extract_frame, text="Extract files (RAR, ZIP)", style='Warning.TLabel')
extract_label.pack(padx=5, pady=10)

# Keyword Listbox
keyword_listbox = tk.Listbox(extract_frame, selectmode=tk.MULTIPLE)
keyword_listbox.pack(pady=10)

for keyword in DEFAULT_KEYWORDS:
    keyword_listbox.insert(tk.END, keyword)

# Keyword Entry
keyword_entry = ttk.Entry(extract_frame)
keyword_entry.pack(pady=5)

keyword_add_button = ttk.Button(extract_frame, text="Add Keyword", command=add_keyword)
keyword_add_button.pack(pady=5)

# 체크박스 한 줄에 배치
check_buttons_frame = Frame(extract_frame)
check_buttons_frame.pack(padx=10, pady=5)

rar_var = IntVar()
rar_checkbutton = ttk.Checkbutton(check_buttons_frame, text="RAR", variable=rar_var, style='Primary.TCheckbutton')
rar_checkbutton.pack(side=tk.LEFT, padx=10, pady=5)

zip_var = IntVar()
zip_checkbutton = ttk.Checkbutton(check_buttons_frame, text="ZIP", variable=zip_var, style='Primary.TCheckbutton')
zip_checkbutton.pack(side=tk.LEFT, padx=10, pady=5)

all_var = IntVar()
all_checkbutton = ttk.Checkbutton(check_buttons_frame, text="All", variable=all_var, style='Primary.TCheckbutton')
all_checkbutton.pack(side=tk.LEFT, padx=10, pady=5)

'''
# Floodgauge 추가
progress_frame = Frame(extract_frame)
progress_frame.pack(padx=10, pady=5, fill='both', expand=True)

floodgauge = Floodgauge(progress_frame, bootstyle=LIGHT, max=100, value=0)
floodgauge.pack(fill='both', expand=True)
'''

# 압축 해제 및 취소 버튼
buttons_frame = Frame(extract_frame)
buttons_frame.pack(padx=10, pady=5)

extract_button = ttk.Button(buttons_frame, text="Extract", command=extract_files, style='Primary.TButton')
extract_button.pack(side=tk.LEFT, padx=10, pady=5)

extract_cancel_button = ttk.Button(buttons_frame, text="Cancel", command=cancel_extraction, style='Secondary.TButton')
extract_cancel_button.pack(side=tk.LEFT, padx=10, pady=5)

### util 프레임 
util_frame = LabelFrame(tab1, text='Utility')  # 탭1에 프레임 추가
util_frame.pack(side=tk.RIGHT, padx=20, pady=10, fill='y')  # 프레임 외부여백

delempty_label = ttk.Label(util_frame, text="*Delete Empty Folders", style='Warning.TLabel')
delempty_label.pack(padx=1, pady=1)

delempty_button = ttk.Button(util_frame, text="Delete Empty Folders", command=delete_empty_folders, style='Primary.TButton')
delempty_button.pack(padx=10, pady=10)

delextract_label = ttk.Label(util_frame, text="*Delete All RAR, ZIP Files", style='Warning.TLabel')
delextract_label.pack(padx=1, pady=1)

delextract_button = ttk.Button(util_frame, text="Delete Extract Files", command=delete_all_rar, style='Primary.TButton')
delextract_button.pack(padx=10, pady=10)

comfiles_label = ttk.Label(util_frame, text="*Move files to new directory (Date)", style='Warning.TLabel')
comfiles_label.pack(padx=1, pady=1)

comfiles_button = ttk.Button(util_frame, text="Compose Files", command=move_files_to_new_directory, style='Primary.TButton')
comfiles_button.pack(padx=10, pady=10)



root.mainloop()

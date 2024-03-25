import os
import datetime
import subprocess
import shutil
import logging
import pathlib
import queue
import json
import sys
import tkinter as tk
import ttkbootstrap as ttk
import tkinter.messagebox as messagebox
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askdirectory, askopenfilename
from ttkbootstrap.constants import *
from ttkbootstrap import Style, utility
from ttkbootstrap.widgets import Floodgauge
from datetime import datetime
from queue import Queue
from threading import Thread

current_process = None  # 현재 실행 중인 프로세스를 추적하기 위한 변수
DEFAULT_KEYWORDS = ["KR*", "[KR]*", "*[KR]*"]

selected_site = None # site_listbox에서 선택된 사이트를 기록하는 변수
default_sites = ['oracle', 'alba', 'saram', 'face', 'insta', 'naver', 'afreeca', 'q-net', 'kakao', 'daum', 'a-bly', 'nexon', 'genshin', 'plaync']


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

    completed_count = 0  # 완료된 작업 수를 저장하는 변수

    total_files = sum(1 for file in os.listdir('.') if
                      (rar_selected or all_selected) and (file.endswith('.rar') or file.endswith('.RAR')) or
                      (zip_selected or all_selected) and (file.endswith('.zip') or file.endswith('.ZIP')))

    progress_step = 100 / total_files  # 각 파일에 대한 진행 상황의 단계

    # 프로그래스 바 업데이트
    progressbar.start()

    for file in os.listdir('.'):
        if rar_selected or all_selected and (file.endswith('.rar') or file.endswith('.RAR')):
            selected_keywords = keyword_listbox.curselection()
            keywords = [keyword_listbox.get(idx) for idx in selected_keywords]
            # 사용자가 선택한 키워드를 적절한 형식으로 조합하여 압축 해제 명령어를 생성
            keyword_string = ' '.join([f"'{keyword}'" for keyword in keywords])
            rar_command = f"mkdir '{file[:-4]}' && 7z x '{file}' -o'{file[:-4]}' -r {keyword_string}"  # 432code
            try:
                current_process = subprocess.Popen(rar_command, shell=True)
                current_process.communicate()  # 프로세스가 완료될 때까지 대기
                print(f"{file} 압축 해제 완료")
                completed_count += 1
                progressbar.step(progress_step)  # 프로그래스 바 업데이트
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
                completed_count += 1
                progressbar.step(progress_step)  # 프로그래스 바 업데이트
            except subprocess.CalledProcessError as e:
                print(f"{file} 압축 해제 중 오류 발생:", e)

    # 프로그래스 바 업데이트
    progressbar.stop()

    if completed_count > 0:
        messagebox.showinfo('압축 해제 완료', f'모든 압축 해제가 완료되었습니다. ({completed_count}개의 파일)')



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
##### tab2


def add_site():
    site_name = site_entry.get().strip()
    if site_name:
        site_listbox.insert(tk.END, site_name)
        # site_listbox에 새로운 항목 추가한 후 선택
        site_listbox.select_set(tk.END)
        global selected_site
        selected_site = site_name
        site_entry.delete(0, tk.END)
    
# 분류 작업 수행
def classify_data():
    global selected_site
    selected_indices = site_listbox.curselection()
    if not selected_indices:
        messagebox.showerror('Error', '사이트를 선택하세요.')
        return

    selected_sites = [site_listbox.get(idx) for idx in selected_indices]

    # 사이트에 대한 데이터를 추출하여 저장하는 함수
    def extract_data(site_names):
        current_directory = os.path.dirname(__file__)  # 파이썬 파일이 위치한 디렉토리
        for site_name in site_names:
            # 사이트 파일 생성
            file_path = os.path.join(current_directory, f'{site_name}.txt')
            with open(file_path, 'w') as file:
                file.write(f'Data for {site_name}:\n')
                file.write('------------------------------\n')

            passwords_files = find_passwords_files()  # Passwords.txt 또는 All Passwords.txt 파일 목록 찾기
            for password_file in passwords_files:
                process_password_file(password_file, site_name, file_path)  # 데이터 추출 및 저장

    extract_data(selected_sites)
    messagebox.showinfo('완료', '선택된 사이트에 대한 데이터가 저장되었습니다.')

def find_passwords_files(starting_directory='.'):
    passwords_files = []
    for root, dirs, files in os.walk(starting_directory):
        if 'Passwords.txt' in files:
            passwords_files.append(os.path.join(root, 'Passwords.txt'))
        if 'All Passwords.txt' in files:
            passwords_files.append(os.path.join(root, 'All Passwords.txt'))
    return passwords_files

# Passwords.txt 또는 All Passwords.txt 파일에서 데이터 추출하여 해당 사이트 텍스트 파일에 저장
def process_password_file(passwords_file_path, site_name, site_file_path):
    with open(passwords_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            # (site_name)이 URL: 뒤에 포함 되어 있는 경우
            if site_name in lines[i] and 'URL:' in lines[i]:
                with open(site_file_path, 'a') as output:
                    output.write(f"상위 디렉터리: {os.path.basename(os.path.dirname(passwords_file_path))}\n")
                    block = []
                    while i < len(lines) and not lines[i].startswith('==============='):
                        block.append(lines[i])
                        i += 1
                    output.writelines(block + ['\n'])
                    break
            i += 1



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
extract_frame = LabelFrame(tab1, text='Extract')
extract_frame.pack(side=tk.LEFT, padx=20, pady=20, fill='both', expand=True)

# 압축 해제 관련 요소들 배치
extract_label = ttk.Label(extract_frame, text="Extract Files (RAR, ZIP)", style='Warning.TLabel')
extract_label.pack(padx=5, pady=10)

keyword_listbox = tk.Listbox(extract_frame, selectmode=tk.MULTIPLE)
keyword_listbox.pack(pady=10)
for keyword in DEFAULT_KEYWORDS:
    keyword_listbox.insert(tk.END, keyword)

keyword_entry = ttk.Entry(extract_frame)
keyword_entry.pack(pady=5)

keyword_add_button = ttk.Button(extract_frame, text="Add Keyword", command=add_keyword)
keyword_add_button.pack(pady=5)

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

buttons_frame = Frame(extract_frame)
buttons_frame.pack(padx=10, pady=5)
extract_button = ttk.Button(buttons_frame, text="Extract", command=extract_files, style='Primary.TButton')
extract_button.pack(side=tk.LEFT, padx=10, pady=5)
extract_cancel_button = ttk.Button(buttons_frame, text="Cancel", command=cancel_extraction, style='Secondary.TButton')
extract_cancel_button.pack(side=tk.LEFT, padx=10, pady=5)

# 유틸리티 관련 요소들 배치
util_frame = LabelFrame(tab1, text='Utility')
util_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill='both', expand=True)

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

# 프로그래스 바 추가
progress_frame = Frame(tab1)
progress_frame.pack(padx=10, pady=5, fill='both', expand=True)
progressbar = ttk.Progressbar(progress_frame, mode='determinate', maximum=100, style='success.Striped.Horizontal.TProgressbar')
progressbar.pack(fill='both', expand=True)

# tab2
filter_frame = LabelFrame(tab2, text='Filter')
filter_frame.pack(padx=20, pady=20, fill='both', expand=True)

filter_label = ttk.Label(filter_frame, text="Filtering on Password.txt to Sites Keyword.", style='Warning.TLabel')
filter_label.pack(padx=5, pady=10)

site_listbox = tk.Listbox(filter_frame, selectmode=tk.MULTIPLE, width=30, height=10)
site_listbox.pack(padx=10, pady=10)
for site in default_sites:
    site_listbox.insert(tk.END, site)

site_entry = ttk.Entry(filter_frame, width=30)
site_entry.pack(pady=5)

site_add_button = ttk.Button(filter_frame, text="Add Site", command=add_site)
site_add_button.pack(pady=5)

classify_button = ttk.Button(filter_frame, text="Classify", command=classify_data, style='Secondary.TButton')
classify_button.pack(pady=5)


root.mainloop()

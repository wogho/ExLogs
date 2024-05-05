import os

# 합칠 파일들이 있는 폴더의 경로
folder_path = '.'

# 결과를 저장할 합칠 파일 경로
output_file_path = './Passwords_combined.txt'

# 모든 폴더 탐색
for root, dirs, files in os.walk(folder_path):
    for file in files:
        # 파일 이름이 'Passwords.txt'인 파일을 찾음
        if file == 'Passwords.txt':
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                # 찾은 파일의 내용을 합칠 파일에 추가
                with open(output_file_path, 'a', encoding='utf-8') as output_file:
                    output_file.write(f.read())
                    output_file.write('\n')  # 각 파일의 내용을 구분하기 위해 줄바꿈 추가

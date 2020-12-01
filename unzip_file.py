import zipfile
import os


zip_file_path = 'task_backend_developer_november_2020.zip'
unzip_data_path = 'unziped_files'

try:
    os.mkdir(unzip_data_path)
    print(f'Folder {unzip_data_path} created.')
except:
    print(f'Folder {unzip_data_path} already exists.')

with zipfile.ZipFile(zip_file_path, 'r') as f:
    f.extractall(unzip_data_path)
    
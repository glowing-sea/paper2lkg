import os
import glob
from pathlib import Path
import shutil

CURRENT_DIR = Path(__file__).parent.resolve()

def resolve_path(path):
    return str(CURRENT_DIR / path)

def clear_folder(folder_path):
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f'{file_name} deleted')
    except Exception as e:
        print(e)



def clear_folder_plus(folder_path):
    try:
        shutil.rmtree(folder_path)  # Deletes the folder and all its contents
        print(f'Folder {folder_path} and its contents have been deleted')
    except Exception as e:
        print(f'Error: {e}')



def clear_specific_files(folder_path, file_pattern):
    try:
        for file_name in glob.glob(os.path.join(folder_path, file_pattern)):
            os.remove(file_name)
            print(f'{file_name} deleted')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    folders_1 = [
        't2_kg_to_text/logs',
        't3_qa/logs',
        'utilities/__pycache__',
    ]

    
    for folder in folders_1:
        clear_folder_plus(resolve_path(folder))

    folders_2 = [
    ]

    for folder in folders_2:
        clear_specific_files(resolve_path(folder), 'kg_*.json')

    
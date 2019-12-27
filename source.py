from typing import NamedTuple
from hashlib import sha256
from pathlib import Path
import sys

BUF_SIZE = 2 ** 16  # 65536


class File(NamedTuple):
    name: str
    path: str


def file_hash(path: str) -> str:
    partial_hash = sha256()
    with open(path, 'rb') as item:
        while True:
            data = item.read(BUF_SIZE)
            if not data:
                break
            partial_hash.update(data)
    return partial_hash.hexdigest()


def merge(what: dict, target: dict) -> dict:
    for key, value in what.items():
        if key not in target.keys():
            target[key] = []
        target[key].append(value)
    return target


def file_accessible(path: str) -> bool:
    try:
        with open(path) as f:
            pass
        return True
    except OSError:
        return False


def get_file_hashes(directory: str, is_recursive: bool = True, depth: int = 0) -> dict:
    directory = Path(directory)
    if not directory.is_dir():
        raise Exception()
    result = {}
    for name in directory.iterdir():
        path = directory / name
        if path.is_dir() and is_recursive and depth < 100:
            result = merge(get_file_hashes(path, is_recursive, depth + 1), result)
        elif not path.is_dir():
            current_hash = file_hash(path)
            if current_hash not in result.keys():
                result[current_hash] = []
            if current_hash in result.keys():
                pass
            result[current_hash].append(File(path.name, str(path.absolute()).replace('\\', '/')))
    return result


def output(files: dict):
    flag = False
    for key in files.keys():
        if len(files[key]) > 1:
            flag = True
            print('/>>>')
            for value in files[key]:
                print('| ', value)
            print('/>>>')
    if flag is False:
        print('No duplicates found!')


if len(sys.argv) > 1:
    start_path = sys.argv[1]
else:
    start_path = input('Path to the directory to scan: ')
while start_path is None or len(start_path) == 0 or not Path(start_path).is_dir() or not Path(start_path).exists():
    start_path = input('Wrong path. "{0}" does not exist or is not a directory. New path: '.format(start_path))

recursive = None
if len(sys.argv) > 2:
    if sys.argv[2].lower() == 'y':
        recursive = True
    elif sys.argv[2].lower() == 'n':
        recursive = False
while recursive is None:
    user_input = input('Check inner directories? y/n (Yes/No): ').lower()
    if user_input == 'y':
        recursive = True
    elif user_input == 'n':
        recursive = False

print('Scanning files in "{0}" '.format(start_path) + ('with' if recursive else 'without') + ' inner directories...')
output(get_file_hashes(start_path, recursive))

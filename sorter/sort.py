from threading import Thread, RLock
from concurrent.futures import ThreadPoolExecutor
from time import time
import logging
import sys
import shutil
import uuid
from pathlib import Path


CATEGORIES = {
    "images": ["JPEG", "PNG", "JPG", "SVG"],
    "video": ["AVI", "MP4", "MOV", "MKV"],
    "documents": ["DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"],
    "audio": ["MP3", "OGG", "WAV", "AMR"],
    "archives": ["ZIP", "GZ", "TAR"],
    "other": [],
}

PROCESS_RESULTS = {"known_extentions": set(), "unknown_extentions": set()}

TEST_MODE = False


def execution_time(func):
    def inner(*args, **kwargs):
        if TEST_MODE:
            timer = time()

        result = func(*args, *kwargs)

        if TEST_MODE:
            logging.debug(f"Execution time of '{func.__name__}' is {time() - timer}")

        return result

    return inner


def get_category(path: Path) -> str:
    category = "other"

    suffix = path.suffix.replace(".", "").upper()

    for cat, ext in CATEGORIES.items():
        if suffix in ext:
            category = cat

    return category


def normalized(name: str) -> str:
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a","b","v","g","d","e","e","j","z","i","j","k","l","m","n","o","p","r","s","t","u","f","h","ts","ch","sh","sch","","y","","e","yu","ya","je","i","ji","g",)

    BAD_SYMBOLS = ["#","%","&","{","}","\\","\<","\>","\*","\?",""," ","$","\!",'"',"'",":","@","+","|","=",]

    TRANS = {}

    for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = t
        TRANS[ord(c.upper())] = t.upper()

    def translate(name: str) -> str:
        new_name = ""

        for i in name:
            new_name += TRANS.get(ord(i), i if i not in BAD_SYMBOLS else "_")

        return new_name

    return translate(name)


def write_process_result(key: str, value: str) -> None:
    new_set = set()
    res_set = PROCESS_RESULTS.get(key, new_set)
    res_set.add(value)
    PROCESS_RESULTS[key] = res_set


def moove_file(root_dir: Path, path: Path, category: str) -> None:
    target_dir = root_dir.joinpath(category)

    if not target_dir.exists():
        target_dir.mkdir()

    new_name = f"{normalized(path.stem)}{path.suffix}"
    new_pass = target_dir.joinpath(new_name)
    if new_pass.exists():
        new_name = f"{normalized(path.stem)}_{uuid.uuid4()}{path.suffix}"
        new_pass = target_dir.joinpath(new_name)

    path.replace(new_pass)

    write_process_result(category, new_name)


def process_file(root_dir: Path, path: Path, locker: RLock):
    with locker:
        if path.is_file() and not len(set(path.parts) & set(CATEGORIES)):
            category = get_category(path)

            if category == "other":
                write_process_result("unknown_extentions", path.suffix)
            else:
                write_process_result("known_extentions", path.suffix)

            moove_file(root_dir, path, category)

@execution_time
def process_files(root_dir: Path) -> None:
    structure = root_dir.glob("**\*")

    locker = RLock()

    threads = []
    
    for path in structure:
        th = Thread(name='process_file', target=process_file, args=(root_dir, path, locker))
        th.start()
        threads.append(th)
        
    # wait for finishing all of threads
    [el.join() for el in threads]


def delete_empty_folders_recursion(path: Path) -> bool:
    is_empty = True

    for child in path.iterdir():
        if child.is_dir():
            is_empty = delete_empty_folders_recursion(child)
        else:
            return False

    if is_empty:
        path.rmdir()

@execution_time
def delete_empty_folders(root_dir: Path) -> None:
    child_list = []
    for child in root_dir.iterdir():
        if child.is_dir():
            child_list.append(child)
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(delete_empty_folders_recursion, child_list)


def extract_archive(path: Path, locker: RLock) -> None:
    with locker:
        try:
            shutil.unpack_archive(path, path.with_name(path.stem), path.suffix.replace(".", ""))
            path.unlink()
        except shutil.ReadError:
            logging.debug(f"Can't unpack file '{path}'!")

@execution_time
def extract_archives(root_dir: Path):
    arch_cat = "archives"
    cat_list = CATEGORIES.get(arch_cat)
    
    if len(cat_list):
        cat_str = " ".join(cat_list)
        pattern = f"{arch_cat}\*.[{cat_str}]*"
        structure = root_dir.glob(pattern)

        locker = RLock()

        threads = []
        
        for path in structure:
            th = Thread(name='extract_archive', target=extract_archive, args=(path, locker))
            th.start()
            threads.append(th)

        # wait for finishing all of threads
        [el.join() for el in threads]


def read_process_result():
    result = ""

    for key, value in PROCESS_RESULTS.items():
        if len(value):
            # text = ", ".join(value).lower()
            text = "\n\t\t".join(value).lower()
            # result += f"{key}: {text}\n"
            result += f"{key}:\n\t\t{text}\n"

    return result


def main():
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")
    
    try:
        root_dir = Path(sys.argv[1]) # for testing C:/Users/Admin/Desktop/test_folder
    except IndexError:
        print(f"You mast enter parameter 'path to folder'. Command example: python {sys.argv[0]} [pathToFolder]")
        return False

    if not root_dir.exists():
        print(f"Path to folder {sys.argv[1]} is not exists")

    # enable/disable "execution_time" test mode
    if len(sys.argv) > 2 and sys.argv[2] == "-t":
        global TEST_MODE
        TEST_MODE = True
    
    process_files(root_dir)
    delete_empty_folders(root_dir)
    extract_archives(root_dir)
    
    result = read_process_result()

    if result:
        print(result)
    else:
        print("No changes was made!")


if __name__ == "__main__":
    main()

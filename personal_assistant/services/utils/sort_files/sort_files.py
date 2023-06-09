import re
import os
from pathlib import Path
import shutil

from colorama import Fore

from .constants import (
    DIR_SUFF_DICT,
    TRANS, FOUND_FILES
)


def sort(path: Path) -> None:
    file_extensions = {}
    other_file_extensions = [0, set()]

    for el in path.iterdir():
        
        if el.is_file():
            folder_name = file_moderation(el, path)

            if folder_name:
                file_extensions[el.suffix] = (file_extensions[el.suffix]+1) if file_extensions.get(el.suffix) else 1
                
            else:
                other_file_extensions[0] += 1
                other_file_extensions[1].add(el.suffix)

        else:
            folder_moderation(el)

    report_folder(path, file_extensions, other_file_extensions)


def file_moderation(file: Path, path: Path) -> str | None:

    for folder_name, suffixes in DIR_SUFF_DICT.items():
        if file.suffix.lower() in suffixes:

            FOUND_FILES[folder_name].append(file.name)

            folder = path.joinpath(folder_name)

            folder.mkdir(exist_ok=True)

            file = file.rename(
                    f"{folder.joinpath(normalize(file.name.removesuffix(file.suffix)))}{file.suffix}"
                )

            if folder_name == "archives":
                archive_folder = folder.joinpath(file.name.removesuffix(file.suffix))
                archive_folder.mkdir(exist_ok=True)

                try:
                    shutil.unpack_archive(
                        file, 
                        archive_folder
                    )
                except (shutil.ReadError, RuntimeError) as e:
                    print(
                        f"{Fore.RED}An error occurred: {e}\n"
                        f"An attempt to extract the archive failed: {Fore.MAGENTA}{file.absolute()}")
            
            return folder_name
    
    else:
        FOUND_FILES["unknown"].append(file.name)

        file.rename(
            f"{path.joinpath(normalize(file.name.removesuffix(file.suffix)))}{file.suffix}"
        )

    
def folder_moderation(folder: Path) -> None:
    if not os.listdir(folder):
        folder.rmdir()

    elif folder.name not in DIR_SUFF_DICT.keys():
        sort(
            folder.rename(
                    f"{str(folder.absolute()).removesuffix(folder.name)}{normalize(folder.name)}"
                )
            )


def normalize(name: str) -> str:
    return re.sub(r'([^\w\s]+)', lambda match: '_' * len(match.group()), name).translate(TRANS)


def report_folder(path: Path, file_extensions: dict, other_file_extensions: list) -> None:

    print(f"{Fore.GREEN}\nIn directory {Fore.MAGENTA}«{path}»{Fore.GREEN} found files with extension:\n"
          f"{Fore.MAGENTA}{'Extension':^15}{Fore.GREEN}|{Fore.MAGENTA}{'Quantity':>5}")

    for extension, quantity in file_extensions.items():
        print(f"{Fore.CYAN}{str(extension):^15}{Fore.GREEN}|{Fore.CYAN}{str(quantity):>5}")

    if other_file_extensions[0]:
        print(
            f"{Fore.CYAN}{other_file_extensions[0]}{Fore.GREEN} files with an unknown extension: "
            f"{Fore.CYAN}{', '.join(other_file_extensions[1])}\n")

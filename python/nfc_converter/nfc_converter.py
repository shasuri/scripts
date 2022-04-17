import os
import sys
import argparse
from typing import List
import unicodedata

def get_converted_string(string_convert: str):
    converted_string = unicodedata.normalize('NFC',string_convert)
    return converted_string

def convert_texts(text_list: List[str]):
    converted_string_list = [get_converted_string(t) for t in text_list]
    return converted_string_list

def convert_save_file_name(file_path_list: List[str]) -> None:
    renamed_count = 0
    print("Renamed : ",end='')
    for file_path in file_path_list:
        file_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)

        converted_file_name = get_converted_string(file_name)
        new_file_path = os.path.join(dir_name,converted_file_name)

        os.rename(file_path,new_file_path)
        renamed_count += 1
        
        if renamed_count != 1:
            print("\t  ",end='')
        print(f"{file_name} -> {converted_file_name}")
    print(f"{renamed_count} file names fixed.")

def execute_script(arguments: argparse.Namespace):
    if(arguments.file != None):
        arguments.file(arguments.strings_convert)

    if(arguments.text != None):
        arguments.text(arguments.strings_convert)

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()

    parser.add_argument("strings_convert",metavar='F', type=str, nargs='+',
        help="Separated file names to fix.")

    parser.add_argument("-f","--file", action='store_const',
        const=convert_save_file_name,
        help="Fix the separated file names and save (default)")

    parser.add_argument("-t","--text", action='store_const',
        const=convert_texts,
        help="Fix the separated texts and print")
    
    args = parser.parse_args()
    
    execute_script(args)

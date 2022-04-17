import sys
import argparse
from typing import List
import unicodedata

def get_converted_string(string_convert: str):
    converted_string = unicodedata.normalize('NFC',string_convert)
    return converted_string

def convert_strings(string_list: List[str]):
    converted_string_list = [get_converted_string(s) for s in string_list]
    return converted_string_list

def convert_save_file_name():
    pass

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()

    parser.add_argument("file_names",metavar='F', type=str, nargs='+',
    help="Separated file names to fix.")

    parser.add_argument("-f","--file", action='store_const',
    default=convert_save_file_name, const=convert_save_file_name,
    help="Fix the separated file names and save (default)")

    parser.add_argument("-t","--text", action='store_const',
    const=convert_strings,
    help="Fix the separated texts and print")
    
    args = parser.parse_args()
    print(args)
    print(args.text(args.file_names))

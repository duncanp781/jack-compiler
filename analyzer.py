"""
analyzer.py

Responsible for the file handling, so this is called from the cli, and returns the outputs
"""

import argparse
import re
import os
import jack_xml
import tokenizer
from compiler import Compiler

class Analyzer:
    def __init__(self, file):
        self.file = self.process_file(file)

    def tokenize(self):
        tokenize = tokenizer.Tokenizer(self.file)
        return tokenize.tokenize(self.file)

    def test_tokenizer(self):
        tokenized = self.tokenize()
        token_xml = [token.toXML() for token in tokenized]
        return jack_xml.XML("tokens", token_xml).display()
    
    def compile(self):
        compiler = Compiler(self.file)
        return compiler.compileClass()

    def process_file(self, file):
        """
        Removes comments and whitespace from file
        """
        #Matches anything like /** ... */ or /* ... */ (or more *)
        file_lines = file.split("\n")

        filtered_lines =[re.sub("\/\/.*", "", line) for line in file_lines]
        no_singleline_comment = " ".join(filtered_lines)
        no_multiline_comments = re.sub("\/\*+.*?\*\/", "", no_singleline_comment) 

        return no_multiline_comments
    
def compileFile(file_path):
    """Processes a .jack file"""
    with open(file_path, 'r') as f: 
        analyzer = Analyzer(f.read())
    
    out_file_path = os.path.splittext(file_path)[0] + '.xml'
    with open(out_file_path, 'w') as o:
        o.write(analyzer.compile())
 
def main():
    parser = argparse.ArgumentParser(description="Process .jack files")
    parser.add_argument('filename', help="The name of the file to process")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Path to a .jack file.', type=str)
    group.add_argument('-d', '--directory', help='Path to directory containing .jack files.', type=str)

    args = parser.parse_args()

    if args.file:
        # If a file path is provided, check if it's a .jack file.
        if args.file.endswith('.jack'):
            compileFile(args.file)
        else:
            print(f"{args.file} is not a .jack file. Skipping.")
    elif args.directory:
        # If a directory path is provided, process all .jack files in that directory.
        if os.path.isdir(args.directory):
            for root, dirs, files in os.walk(args.directory):
                for file in files:
                    if file.endswith('.jack'):
                        compileFile(os.path.join(root, file))
        else:
            print(f"{args.directory} is not a valid directory. Exiting.")

    with open(args.filename, 'r') as f:
        file_content = f.read()


if __name__ == "__main__":
    main()

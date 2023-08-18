"""
analyzer.py

Responsible for the file handling, so this is called from the cli, and returns the outputs
"""

import argparse
import tokenizer
import jack_xml
import re
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
    
    def test_compiler(self):
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
 
def main():
    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument('filename', help="The name of the file to process")

    args = parser.parse_args()

    with open(args.filename, 'r') as f:
        file_content = f.read()

    analyzer = Analyzer(file_content)
    analyzer.process_file(file_content)
    compiled_result = analyzer.test_compiler()

    with open('test.xml', 'w') as f:
        f.write(compiled_result.display())

   # with open('test.xml', 'w') as f:
        #if.write(tokenized_result)

if __name__ == "__main__":
    main()

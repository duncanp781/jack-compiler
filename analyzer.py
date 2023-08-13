"""
analyzer.py

Responsible for the file handling, so this is called from the cli, and returns the outputs
"""

import argparse
import tokenizer
import jack_xml
import re

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

    def process_file(self, file):
        """
        Removes comments and whitespace from file
        """
        #Matches anything like /** ... */ or /* ... */ (or more *)
        no_multiline_comments = re.sub("\/\*+.*?\*\/", "", file) 
        file_lines = no_multiline_comments.split("\n")

        filtered_lines =[line.strip() for line in file_lines if not re.match("\/\/.*", line)]

        return " ".join(filtered_lines)
 
def main():
    parser = argparse.ArgumentParser(description="Process an input file.")
    parser.add_argument('filename', help="The name of the file to process")

    args = parser.parse_args()

    with open(args.filename, 'r') as f:
        file_content = f.read()

    analyzer = Analyzer(file_content)
    analyzer.process_file(file_content)
    tokenized_result = analyzer.test_tokenizer()

    with open('test.xml', 'w') as f:
        f.write(tokenized_result)

if __name__ == "__main__":
    main()

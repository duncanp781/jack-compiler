"""
analyzer.py

Responsible for the file handling, so this is called from the cli, and returns the outputs
"""

import tokenizer
import jack_xml

class Analyzer:
    def __init__(self, file):
        file = file

    def tokenize(self):
        tokenizer = tokenizer.Tokenizer()
        return tokenizer.tokenize(" ".split(self.file))

    def test_tokenizer(self):
        tokenized = self.tokenize()
        token_xml = [token.toXML() for token in tokenized]
        return jack_xml.XML("tokens", token_xml)
    
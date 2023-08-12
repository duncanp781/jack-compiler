import jack_xml


class Token:
    def __init__(self, type, content):
        type = type
        content = content
    
    def toXML(self):
        return jack_xml.XML(self.type, self.content)

class Tokenizer:
    KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', \
                'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',  \
                'let', 'do', 'if', 'else', 'while', 'return'}
    
    SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}

    TOKENTYPE = {'keyword', 'symbol', 'identifier', 'integerConstant', 'stringConstant'}

    def __init__(self, file):
        file_array = file.split(" ")

    def splitIntoTokens(string):
        """
        Given a string, split it into array of strings, each of which is one token
        Used for cases when we have multiple tokens not separated by a space, e.g. 'foo()' -> ['foo', '(', ')']
        """
        pass

    def getToken(string):
        """
        Given a string that contains one token, return the token of that string
        Throws an error if string is more than one token, so process the string with splitIntoTokens before
        """
        pass


import re
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

    def __init__(self):
        pass

    def splitIntoTokens(self, string):
        """
        Given a string, split it into array of strings, each of which is one token
        Used for cases when we have multiple tokens not separated by a space, e.g. 'foo()' -> ['foo', '(', ')']
        """
        #Funny regex to match a string like Bar.foo.baz(test) and split it into groups Bar.foo.baz, (, test, )
        pattern = "^([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)(\()([^)]*)(\))$"
        match = re.match(pattern, string) 
        if match:
            group_list = list(match.group())
            if len(group_list) > 3:
                #If this is longer than 3, then we have something like a(b), and we also need to split b into tokens, since it can be a nested function
                inner_groups = self.splitIntoTokens(match.group(3))
                if isinstance(inner_groups, list):
                    return [match.group(1), match.group(2)] + inner_groups + [match.group(4)]
                else:
                    return group_list()

        else:
            return [string]
    
    def processFileEntries(self, file_array):
        """
        Given a file array (file split by " "), split any multi-token entries into the individual tokens
        Applies splitIntoTokens to each entry, flattening the resulting list
        """
        out = []
        for entry in file_array:
            entry_processed = self.splitIntoTokens(entry)
            out = out + entry_processed
        return out

    def getToken(self, string):
        """
        Given a string that contains one token, return the token of that string
        Throws an error if string is more than one token, so process the string with splitIntoTokens before
        """
        if string in self.KEYWORDS:
            return Token('keyword', string)
        if string in self.SYMBOLS:
            return Token('symbol', string)
        if re.match('\d+', string): #Match any integer
            return Token('integerConstant', string)
        if re.match('".*?"'): #Match anything like "...". Don't allow " in strings, so greedy match to the first quote.
            return Token("stringConstant", string[1:-1]) #Dont include the " " 
        if re.match('[a-zA-Z_]\w*', string):
            return Token("Identifier", string)
        else:
            raise Exception

    def tokenize(self, arr):
        """
        Given an array of strings, return an array of the corresponding tokens
        Applies processFileEntries, then getToken to each entry
        """
        processed_arr = self.processFileEntries(arr)
        out = []
        for stringToken in processed_arr:
            out.append(self.getToken(stringToken))
        return out
 
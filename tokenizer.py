import re
import jack_xml


class Token:
    def __init__(self, type, content):
        self.type = type
        self.content = content
    
    def toXML(self):
        return jack_xml.XML(self.type, self.content)
    
    def checkContent(self, compare):
        '''
        Checks if the content of the token matches what is in compare

        compare - a string or a list
        '''
        if isinstance(compare, list):
            return self.content in compare
        else:
            return self.content == compare
    
    def checkType(self, compare):
        '''
        Checks if the type of the token matches what is in compare
        '''
        
        if isinstance(compare, list):
            return self.type == compare
        else:
            return self.type == compare

class Tokenizer:
    KEYWORDS = frozenset(('class', 'constructor', 'function', 'method', 'field', 'static', 'var', \
                'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',  \
                'let', 'do', 'if', 'else', 'while', 'return'))
    
    SYMBOLS = frozenset(('{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'))

    TOKENTYPE = frozenset(('keyword', 'symbol', 'identifier', 'integerConstant', 'stringConstant'))

    def __init__(self, file):
        self.file = file
    
    def tokenize(self, file):
        """
        Instead of splitting in spaces and trying to process it, lets try to process token by token
        """
        out = []
        i = 0
        while i < len(file):
            #Check for a quote, if so include the whole thing
            if re.match('\".*\".*', file[i:]):
                i += 1
                cur_string = ""
                while file[i] != '"':
                    cur_string = cur_string + file[i]
                    i += 1
                out.append(Token('stringConstant', cur_string))
                i += 1
            #Check for symbol
            elif file[i] in self.SYMBOLS:
                out.append(Token("symbol", file[i]))
                i += 1
            #Check for an integer
            elif re.match("\d", file[i]):
                cur_int = file[i]
                i += 1
                while re.match("\d", file[i]):
                    cur_int = cur_int + file[i]
                    i += 1
                out.append(Token("integerConstant", cur_int))
            else: 
                #Match longest possible identifier (no whitespace / symbols other than _)
                identifier_match = re.match("^[a-zA-Z_]\w*", file[i:])
                if identifier_match:
                    matched = identifier_match.group()
                    #Check if keyword or not
                    if matched in self.KEYWORDS:
                         out.append(Token("keyword", matched))
                    else:
                        #Split based on the periods in the identifeir 
                        #E.g., Foo.bar splits to tokens with Foo, ., and bar
                        last = 0
                        for j , c in enumerate(matched):
                            if c == '.':
                                if last != j:
                                    out.append(Token(type = "identifier", content = matched[last:i]))
                                last = j+1
                                out.append(Token(type = "symbol", content = c))
                            elif j == len(matched) - 1:
                                out.append(Token(type = "identifier", content = matched[last:i+1]))
                        
                    i += len(matched)
                else:
                    if file[i] != " ":
                        print("No matches on: ", file[i:])
                    i += 1
        return out

   
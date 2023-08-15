import jack_xml
from tokenizer import Tokenizer

class Compiler:
    def __init__(self, file):
        self.cur_file = file
        print(file)
        
        tokenizer = Tokenizer(file)
        self.tokens = tokenizer.tokenize(file)
        self.cur_token_index = 0

    def expect(self, parent, content = None, type = None):
        '''
        Specifies and checks what the next token contains. Then selects the next token

        Keyword arguments:
        content - A string or list of strings to check against
        type - A string to check against
        parent - An XML object. If successful, add the token to the parent as a child
        '''
        token = self.tokens[self.cur_token_index]
        if content and type:
            if token.checkContent(content) and token.checkType(type):
                parent.addChild(token.toXML())
            else:
                raise CompileError(f"Expected token of type {type} with content {content}, got type {token.type} and content {token.content}")
        elif content:
            if token.checkContent(content):
                parent.addChild(token.toXML())
            else:
                raise CompileError(f"Expected token with content {content}, got type {token.type} and content {token.content}")
        elif type: 
            if token.checkType(type):
                parent.addChild(token.toXML())
            else:
                raise CompileError(f"Expected token of type {type}, got type {token.type} and content {token.content}")
        self.cur_token_index += 1



    def check(self, content = None, type = None):
        '''
        Check if the next token is of the specified type, returns a boolean
        '''
        token = self.tokens[self.cur_token_index]
        if content and type:
            return token.checkContent(content) and token.checkType(type)
        elif content:
            return token.checkContent(content)
        elif type: 
            return token.checkType(content)
        

    def compileClass(self):
        '''
        Compiles a class with grammar class NAME { ... }
        '''
        classXML = jack_xml.XML(tag = "class")
        self.expect(content = 'class', parent= classXML)
        self.expect(type = 'identifier', parent=classXML)
        self.expect(content = '{', parent=classXML)
        has_var_decs = self.check(content = ['static', 'field'])
        while has_var_decs:
            classXML.addChild(self.compileClassVarDec())
            has_var_decs = self.check(content = ['static', 'field'])
        has_subroutines = self.check(content = ['constructor', 'field', 'method'])
        while has_subroutines:
            classXML.addChild(self.compileSubroutine())
            has_subroutines = self.check(content = ['constructor', 'field', 'method'])
        self.expect(content = '}', parent = classXML)
        return classXML

    def compileClassVarDec(self):
        '''
        Compiles static or field variable declarations
        '''
        pass

    def compileSubroutine(self):
        '''
        Compiles functions, methods, and constructors with grammar function TYPE NAME (...){...}
        '''
        pass
    
    def compileParameterList(self):
        '''
        Compiles a (possible empty) parameter list that looks like (...)
        '''
        pass

    def compileSubroutineBody(self):
        '''
        Compiles a subroutines body
        '''

    def compileVarDec(self):
        '''
        Compiles a var declaration with grammar Var TYPE NAME;
        '''

    def compileStatements(self):
        '''
        Compiles a sequence of statements
        '''
    
    def compileLet(self):
        '''
        Compiles a let statement that looks like let NAME = EXPRESSION;
        '''

    def compileIf(self):
        '''
        Compiles a if statement that may have an else statement with grammar if (condition){ ... }else{ ... }
        '''

    def compileWhile(self):
        '''
        Compiles a while statement with grammar while(condition){...}
        '''

    def compileDo(self):
        '''
        Compiles a do statement with grammar do funcName(params);
        '''

    def compileReturn(self):
        '''
        Compiles a return statement with grammar return (returnValue?);
        '''
    
    #TODO Implement compileExpression, compileTerm, and compileExpressionList

class CompileError(Exception):
    pass

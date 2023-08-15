import jack_xml
from tokenizer import Tokenizer

class Compiler:
    def __init__(self, file):
        self.cur_file = file
        print(file)
        
        tokenizer = Tokenizer(file)
        self.tokens = tokenizer.tokenize(file)
        self.cur_token_index = 0

    def expect(self, parent, content = None, type = None, allowEither = False):
        '''
        Specifies and checks what the next token contains. Then selects the next token

        Keyword arguments:
        content - A string or list of strings to check against
        type - A string or list of strings to check against
        parent - An XML object. If successful, add the token to the parent as a child
        allowEither - A boolean. If true, allow just one of content and type to match - only applies if both content and type are given
        '''
        token = self.tokens[self.cur_token_index]

        if allowEither:
            if content and type and not(token.checkContent(content) or token.checkType(type)):
                raise CompileError(f"Expected token of type {type} with content {content}, got type {token.type} and content {token.content}")
        else:
            if content and type and not(token.checkContent(content) and token.checkType(type)):
                raise CompileError(f"Expected token of type {type} with content {content}, got type {token.type} and content {token.content}")
        
        if content and not token.checkContent(content):
            raise CompileError(f"Expected token with content {content}, got type {token.type} and content {token.content}")
        elif type and not token.checkType(type): 
            raise CompileError(f"Expected token of type {type}, got type {token.type} and content {token.content}")
        
        parent.addChild(token.toXML())
        self.cur_token_index += 1

    def expectType(self, parent):
        '''
        Checks if the current token is an allowable type
        Grammar: 'int'|'char'|'boolean'|className
        Does not check that this is an existing class
        '''
        return self.expect(content = ['int', 'char', 'boolean'], type = 'identifier', parent = parent, allowEither=True)
    
    def expectBody(self, parent, begin = None, end = None, interior = None):
        '''
        Compiles a body that looks like begin (recursive call to interior) end, and appends to parent
        Use, for example, with grammar like '(' body ')' 
        '''
        if begin:
            self.expect(content = begin, parent = parent)
        if interior:
            parent.addChild(interior())
        if end:
            self.expect(content = end, parent = parent)


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
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        '''
        classVarDecs = []

        while self.check(content = ["static", "field"]):
            varDecXML = jack_xml.XML(tag = "classVarDec")
            self.expect(content = ['static', 'field'], parent = varDecXML)
            self.expectType(varDecXML)
            self.expect(type = 'identifier') #varName

            #Check if declaring multiple variables
            while self.check(content = ','):
                self.expect(content = ',', parent = varDecXML)
                self.expect(type = 'identifier', parent = varDecXML) # varName

            self.expect(content= ';', parent=varDecXML)

            classVarDecs.append(varDecXML)

        return classVarDecs

    def compileSubroutine(self):
        '''
        Compiles functions, methods, and constructors 
        Grammar ('constructor'|'function'|'method')('void'|type) subroutineName
        '''
        subroutineDecs = []

        while self.check(content = ['constructor', 'function', 'method']):
            subroutineDecXML = jack_xml.XML(tag = "subroutineDec")
            self.expect(content = ['constructor', 'function', 'method'], parent = subroutineDecXML)

            #Either a type or void
            if self.check(content = 'void'):
                self.expect(content = 'void', parent = subroutineDecXML)
            else:
                self.expectType(subroutineDecXML)
            
            self.expect(type = 'identifier', parent = subroutineDecXML) #subroutineName

            self.expect(content = '(', parent = subroutineDecXML)
            subroutineDecXML.addChild(self.compileParameterList())
            self.expect(content = ')')

            subroutineDecXML.addChild(self.compileSubroutineBody())

            subroutineDecs.append(subroutineDecXML)
        
        return subroutineDecs


    
    def compileParameterList(self):
        '''
        Compiles a (possible empty) parameter list that looks like (...)
        '''
        if self.check(content = ['int', 'char', 'boolean']) or self.check(type = 'identifier'):
            parameterListXML = jack_xml.XML(tag = 'parameterList')
            self.expectType(parameterListXML)
            self.expect(type = 'identifier', parent = parameterListXML)
            while self.check(content = ','):
                self.expect(content = ',', parent = parameterListXML)
                self.expect(type = 'identifier', parent = parameterListXML)
        else:
            return None

    def compileSubroutineBody(self):
        '''
        Compiles a subroutines body
        Grammar: '{' varDec* statements '}'
        '''
        subroutineBodyXML = jack_xml.XML(tag = 'subroutineBody')
        self.expect(content = '{', parent = subroutineBodyXML)
        subroutineBodyXML.addChild(self.compileVarDec())
        subroutineBodyXML.addChild(self.compileStatements())
        self.expect(content = '{', parent = subroutineBodyXML)
        return subroutineBodyXML

    def compileVarDec(self):
        '''
        Compiles a var declaration with grammar Var TYPE NAME;
        Grammar: 'var' type varName (',' varName)* ';'
        '''
        varDecs = []
        while self.check(content = 'var'):
            varDecXML = jack_xml.XML(tag = 'varDec')
            self.expectType(varDecXML)
            while self.check(content = ','):
                self.expect(content = ',', parent = varDecXML)
                self.expect(type = 'identifier', parent = varDecXML)
            self.expect(content = ';')
            varDecs.append(varDecXML)
        
        return varDecs


    def compileStatements(self):
        '''
        Compiles a sequence of statements
        '''
        statements = []
        has_statements = True

        while has_statements:
            token = self.tokens[self.cur_token_index]
            match token.content:
                case 'let':
                    statements.append(self.compileLet())
                case 'if':
                    statements.append(self.compileIf())
                case 'while':
                    statements.append(self.compileWhile())
                case 'do':
                    statements.append(self.compileDo())
                case 'return':
                    statements.append(self.compileReturn())
                case _:
                    has_statements = False

        return statements
    
    def compileLet(self):
        '''
        Compiles a let statement that looks like let NAME = EXPRESSION;
        '''
        letXML = jack_xml.XML(tag = 'letStatement')
        self.expect(content = 'let', parent = letXML)
        self.expect(type = 'identifier')
        if self.check(content = '['):
            self.expectBody(begin = '[', end = ']', interior = self.compileExpression, parent = letXML)
        self.expect(content = '=', parent = letXML)
        letXML.addChild(self.compileExpression())
        self.expect(content = ';', parent = letXML)
        return letXML

    def compileIf(self):
        '''
        Compiles a if statement that may have an else statement with grammar if (condition){ ... }else{ ... }
        '''
        ifXML = jack_xml.XML(tag = 'ifStatement')
        self.expect(content = 'if', parent = ifXML)
        self.expectBody(begin = '(', end = ')', interior = self.compileExpression, parent = ifXML)
        self.expectBody(begin = '{', end = '}', interior = self.compileStatements, parent = ifXML)
        if self.check(content = 'else'):
            self.expect(content = 'else', parent = ifXML)
            self.exepctBody(begin = '{', end = '}', interior = self.compileStatements, parent = ifXML)
        return ifXML
        

    def compileWhile(self):
        '''
        Compiles a while statement with grammar while(condition){...}
        '''
        whileXML = jack_xml.XML(tag = 'whileStatement')
        self.expect(content = 'while', parent = whileXML)
        self.expectBody(begin = '(', end = ')', interior = self.compileExpression, parent = whileXML)
        self.expectBody(begin = '{', end = '}', interior = self.compileStatements, parent = whileXML)
        return whileXML

    def compileDo(self):
        '''
        Compiles a do statement with grammar do funcName(params);
        '''
        doXML = jack_xml.XML(tag = 'doStatement')
        self.expect(content = 'do', parent = doXML)
        #EXPECT SUBROUTINE CALL
        self.expect(content = ';', parent = doXML)


    def compileReturn(self):
        '''
        Compiles a return statement with grammar return (returnValue?);
        '''
        returnXML = jack_xml.XML(tag = 'returnStatement')
        self.expect(content = 'return', parent = returnXML)
        if self.check(content = ';'):
            self.expect(content = ';', parent = returnXML)
        else:
            returnXML.addChild(self.compileExpression())
            self.expect(content = ';', parent = returnXML)
        return returnXML

    
    def compileExpression(self):
        #NOT IMPLEMENTED: Just assumes there is only one identifier
        expressionXML = jack_xml.XML(tag = 'expression')
        self.expect(type = 'identifier', parent = expressionXML)
        return expressionXML

    def compileTerm(self):
        # NOT IMPLEMENTED
        pass

    def compileExpressionList(self):
        #NOT IMPLEMENTED
        pass

    #TODO Implement compileExpression, compileTerm, and compileExpressionList

class CompileError(Exception):
    pass

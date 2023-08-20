import jack_xml
from tokenizer import Tokenizer

class Compiler:
    def __init__(self, file):
        self.cur_file = file
        
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
                raise CompileError(f"Expected token with either type {type} or content {content}, got type {token.type} and content {token.content}")
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
        #print(f"Expecting content = {content} and type = {type}, got content {token.content} and type {token.type}")
        if content and type:
            return token.checkContent(content) and token.checkType(type)
        elif content:
            return token.checkContent(content)
        elif type: 
            return token.checkType(type)


    def compileClass(self):
        '''
        Compiles a class with grammar class NAME { ... }
        '''
        classXML = jack_xml.XML(tag = "class")
        self.expect(content = 'class', parent= classXML)
        self.expect(type = 'identifier', parent=classXML)
        self.expect(content = '{', parent=classXML)

        classXML.addChild(self.compileClassVarDec())

        classXML.addChild(self.compileSubroutine())

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
            self.expect(type = 'identifier', parent = varDecXML) #varName

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
        Grammar ('constructor'|'function'|'method')('void'|type) subroutineName '(' parameterList ')' subroutineBody
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

            self.expectBody(begin = '(', end = ')', interior = self.compileParameterList, parent = subroutineDecXML)
            subroutineDecXML.addChild(self.compileSubroutineBody())

            subroutineDecs.append(subroutineDecXML)
        
        return subroutineDecs


    
    def compileParameterList(self):
        '''
        Compiles a (possible empty) parameter list that looks like (...)
        '''
        
        parameterListXML = jack_xml.XML(tag = 'parameterList')
        if self.check(content = ['int', 'char', 'boolean']) or self.check(type = 'identifier'):
            self.expectType(parameterListXML)
            self.expect(type = 'identifier', parent = parameterListXML)
            while self.check(content = ','):
                self.expect(content = ',', parent = parameterListXML)
                self.expectType(parent = parameterListXML)
                self.expect(type = 'identifier', parent = parameterListXML)
        return parameterListXML

    def compileSubroutineBody(self):
        '''
        Compiles a subroutines body
        Grammar: '{' varDec* statements '}'
        '''
        subroutineBodyXML = jack_xml.XML(tag = 'subroutineBody')
        self.expect(content = '{', parent = subroutineBodyXML)
        subroutineBodyXML.addChild(self.compileVarDec())
        subroutineBodyXML.addChild(self.compileStatements())
        self.expect(content = '}', parent = subroutineBodyXML)
        return subroutineBodyXML

    def compileVarDec(self):
        '''
        Compiles a var declaration with grammar Var TYPE NAME;
        Grammar: 'var' type varName (',' varName)* ';'
        '''
        varDecs = []
        while self.check(content = 'var'):
            varDecXML = jack_xml.XML(tag = 'varDec')
            self.expect(content = 'var', parent = varDecXML)
            self.expectType(varDecXML)
            self.expect(type = 'identifier', parent = varDecXML)
            while self.check(content = ','):
                self.expect(content = ',', parent = varDecXML)
                self.expect(type = 'identifier', parent = varDecXML)
            self.expect(content = ';', parent = varDecXML)
            varDecs.append(varDecXML)
        
        return varDecs


    def compileStatements(self):
        '''
        Compiles a sequence of statements
        '''
        statements = jack_xml.XML(tag = "statements")
        has_statements = True

        while has_statements:
            token = self.tokens[self.cur_token_index]
            match token.content:
                case 'let':
                    statements.addChild(self.compileLet())
                case 'if':
                    statements.addChild(self.compileIf())
                case 'while':
                    statements.addChild(self.compileWhile())
                case 'do':
                    statements.addChild(self.compileDo())
                case 'return':
                    statements.addChild(self.compileReturn())
                case _:
                    has_statements = False

        return statements
    
    def compileLet(self):
        '''
        Compiles a let statement that looks like let NAME = EXPRESSION;
        '''
        letXML = jack_xml.XML(tag = 'letStatement')
        self.expect(content = 'let', parent = letXML)
        self.expect(type = 'identifier', parent = letXML)
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
            self.expectBody(begin = '{', end = '}', interior = self.compileStatements, parent = ifXML)
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
        self.expect(type = "identifier", parent = doXML)
        while self.check(content = "."):
            self.expect(content = ".", parent = doXML)
            self.expect(type = "identifier", parent = doXML)
        self.expectBody(begin = "(" ,end = ")", interior = self.compileExpressionList, parent = doXML)
        self.expect(content = ';', parent = doXML)
        return doXML

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
        expressionXML.addChild(self.compileTerm())
        if self.check(content = ['+', '-', '*', '/', '&', '|', '<', '>', '=']):
            self.expect(type = 'symbol', parent = expressionXML)
            expressionXML.addChild(self.compileTerm())
        return expressionXML

    def compileTerm(self):
        '''
        Compiles a term.

        Grammar: integerConstant | stringConstant | ['true','false','null','this'] | varName | varName[expression] | subroutineCall | (expression) | ['-','~'] term

        subroutineCall: subroutineName(expressionList) | (className | varName).subroutineName(expressionList)
        '''
        termXML = jack_xml.XML(tag = 'term')
        #Check if is (expression)
        if self.check(content = '('):
            self.expectBody(begin = '(', end = ')', interior = self.compileExpression, parent = termXML)
        #Check types of identifiers
        elif self.check(type = 'identifier'):
            self.expect(type = 'identifier', parent = termXML)
            if self.check(content = '['):
                self.expectBody(begin = '[', end = ']', interior = self.compileExpression, parent = termXML)
            else :
                #A varName can't have a . in it, so only allow that if we are doing a function call - error otherwise
                hasPeriod = False
                while self.check(content = '.'):
                    hasPeriod = True
                    self.expect(content = '.', parent = termXML)
                    self.expect(type = 'identifier', parent = termXML)
                if hasPeriod or self.check(content = '('):
                    self.expectBody(begin = '(', end = ')', interior = self.compileExpressionList, parent = termXML)
        #Check for unaryOp Term
        elif self.check(content = ['-', '~']):
            self.expect(type = 'symbol', parent = termXML)
            termXML.addChild(self.compileTerm())
        #Check for keywordConstant
        elif self.check(content = ['true','false','null','this']):
            self.expect(content = ['true','false','null','this'], parent = termXML)
        else:
            self.expect(type = ['integerConstant', 'stringConstant'], parent = termXML)
        return termXML

    def compileExpressionList(self):
        '''
        Compile a list of expressions
        '''
        expressonListXML = jack_xml.XML(tag = 'expressionList')
        while not self.check(content = ')'):
            expressonListXML.addChild(self.compileExpression())
            while self.check(content = ','):
                self.expect(content = ',', parent = expressonListXML)
                expressonListXML.addChild(self.compileExpression())
        return expressonListXML


class CompileError(Exception):
    pass

"""
jack_xml.py

This is for implementing the xml syntax used by the tokenizer and parser for the compiler.
"""

class XML:
    def __init__(self, tag, content = None):
        """
        Initializes the object.
        - tag (str): the XML tag name
        - content: The content inside the XML tag. It can be either a string, another XML object a list of XML objects, or None
        """
        self.tag = tag
        self.content = content 
        
    def isStringContent(self):
        """Returns whether self.content is a string"""
        return isinstance(self.content, str)

    def isXmlContent(self):
        """Returns whether self.content is an XML object"""
        return isinstance(self.content, XML)
    
    def isXmlListContent(self):
        """Returns whether self.content is a list of XMl""" 
        return isinstance(self.content, list) and all(isinstance(item, XML) for item in self.content)

    def isNone(self):
        return self.content == None

    def addChild(self, child):
        """Adds a child to the current XML content
        Child can be anything content can be, but adding None will do nothing
        Children cant be added if the XML holds string content, it will raise an error
        """
        if child == None or child == []: 
            return
        elif self.isNone():
            self.content = child
        elif isinstance(child, str) or self.isStringContent():
            ###Can't add string as a child unless no content
            raise XMLError()
        elif self.isXmlContent():
            if isinstance(child, list):
                self.content = [self.content] + child
            else:
                self.content = [self.content, child]
        elif self.isXmlListContent():
            if isinstance(child, list):
                self.content = self.content + child
            else:
                self.content.append(child)
        elif self.isNone():
            self.content = child

    def display(self):
        """Returns a string representation of the XML content"""

        if self.isStringContent():
            #These symbols aren't able to be rendered by xml in browsers, so we replace them
            xml_safe_content = self.content
            match self.content:
                case '<':
                    xml_safe_content = '&lt;'
                case '>':
                    xml_safe_content = '&gt;'
                case '"':
                    xml_safe_content = 'quot;'
                case '&':
                    xml_safe_content = '&amp;'

            return f"<{self.tag}> {xml_safe_content} </{self.tag}>"
        
        if self.isXmlContent():
            return f"<{self.tag}>\n\t {self.content.display()} \n</{self.tag}>"

        if self.isXmlListContent():
            children_displayed = '\n\t'.join([subcontent.display() for subcontent in self.content])
            return f'''<{self.tag}>\n\t{children_displayed} \n</{self.tag}>'''

        if self.isNone():
            return f"<{self.tag}>\n</{self.tag}>"
        
class XMLError(Exception):
    """Custom exception for XML-related errors."""
    pass


"""
jack_xml.py

This is for implementing the xml syntax used by the tokenizer and parser for the compiler.
"""

class XML:
    def __init__(self, tag, content):
        """
        Initializes the object.
        - tag (str): the XML tag name
        - content: The content inside the XML tag. It can be either a string, another XML object, or a list of XML objects
        """
        self.tag = tag
        self.content = content 
        
    def is_string_content(self):
        """Returns whether self.content is a string"""
        return isinstance(self.content, str)

    def is_xml_content(self):
        """Returns whether self.content is an XML object"""
        return isinstance(self.content, XML)
    
    def is_xml_list_content(self):
        """Returns whether self.content is a list of XMl""" 
        return isinstance(self.content, list) and all(isinstance(item, XML) for item in self.content)

    def add_child(self, child):
        """Adds a child to the current XML content"""
        if self.is_string_content():
            raise XMLError()
        elif self.is_xml_content():
            self.content = [self.content, child]
        elif self.is_xml_list_content():
            self.content.append(child)

    def display(self):
        """Returns a string representation of the XML content"""
        

            

        if self.is_string_content():
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
        
        if self.is_xml_content():
            return f"<{self.tag}> {self.content.display()} </{self.tag}>\n"

        if self.is_xml_list_content():
            children_displayed = '\n\t'.join([subcontent.display() for subcontent in self.content])
            return f'''<{self.tag}>\n\t{children_displayed}\n</{self.tag}>'''

class XMLError(Exception):
    """Custom exception for XML-related errors."""
    pass


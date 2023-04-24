import abc
import re

# What is the point of this. Why is it here. Does it exist solely to have children?
class Preprocessor(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def preprocess(self, query: str) -> list[str]:
        return []

# Why do we have a class for this when it could just be one single function? 
class SimplePreprocessor(Preprocessor):
    def preprocess(self, query: str) -> list[str]:
        # Creates a list of tokens 
        # Said tokens have any instance of ',', ';', and '/' replaced with 'and'
        # Then splits a string into individual tokens based on individual words or phrases (signified with "")
        tokens: list[str] = re.findall(r'[^"\s]\S*|".+?"', re.sub(r'[,;/]+', ' and ', query))
        # Removes quotes from tokens
        return [token[1:-1].strip() if token[0] == '"' and token[0] == token[-1] else token for token in tokens]
    
    # If we need to keep this as a class, why not also add in removing stop words as another function? 
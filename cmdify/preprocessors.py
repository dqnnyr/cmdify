import abc
import re


class Preprocessor(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def preprocess(self, query: str) -> list[str]:
        return []


class SimplePreprocessor(Preprocessor):
    def preprocess(self, query: str) -> list[str]:
        tokens: list[str] = re.findall(r'[^"\s]\S*|".+?"', re.sub(r'[,;/]+', ' and ', query))
        return [token[1:-1].strip() if token[0] == '"' and token[0] == token[-1] else token for token in tokens]
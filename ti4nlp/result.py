import abc
from typing import Any

class Result:
    __metaclass__ = abc.ABCMeta


class Error(Result):
    __metaclass__ = abc.ABCMeta


class Success(Result):
    def __init__(self, result: Any):
        self.result = result


class Failure(Result):
    def __init__(self, errors: list[Error]):
        self.errors = errors


class UnrecognizedWordError(Error):
    def __init__(self, word: str):
        self.word = word


class AmbiguousWordError(Error):
    def __init__(self, word: str, options: list[str]):
        self.word = word
        self.options = options

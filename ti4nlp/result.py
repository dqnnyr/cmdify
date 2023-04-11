import abc
from typing import Any


class Result:
    __metaclass__ = abc.ABCMeta


class Error:
    __metaclass__ = abc.ABCMeta


class Success(Result):
    """
    Indicates that the function succeeded. The `result` attribute holds the output.
    """
    def __init__(self, result: Any):
        self.result = result


class Failure(Result):
    """
    Indicates that the function failed. The `errors` attribute holds a list of discovered `Error`s.
    """
    def __init__(self, errors: list[Error]):
        self.errors = errors


class UnrecognizedWordError(Error):
    """
    Indicates that there were no appropriate matches for a given word, stored in the `word`.
    """
    def __init__(self, word: str):
        self.word = word


class AmbiguousWordError(Error):
    """
    Indicates that multiple matches were equally appropriate for a given word. The word is stored in the `word`
    attribute, and the possible canonical representations are stored in the `options` attribute.
    """
    def __init__(self, word: str, options: list[str]):
        self.word = word
        self.options = options


class UnclassifiedWordError(Error):
    """
    Indicates a mismatch between the Processor's `WordClassifier` and the underlying Identifier's `WordIndex`, as the
    WordIndex returned a canonical representation that was not classified. The offending word is stored in the `word`
    attribute.
    """
    def __init__(self, word: str):
        self.word = word

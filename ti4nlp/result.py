import abc


class Result:
    __metaclass__ = abc.ABCMeta


class Success(Result):
    def __init__(self, result):
        self.result = result


class Failure(Result):
    def __init__(self, errors):
        self.errors = errors


class UnrecognizedWordError(Result):
    def __init__(self, word):
        self.word = word


class AmbiguousWordError(Result):
    def __init__(self, word, options):
        self.word = word
        self.options = options

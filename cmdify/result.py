import abc
from typing import Any

class Result(abc.ABC):
    pass


class Error(abc.ABC):
    pass


class Success(Result):
    """Indicates that the function succeeded. The `result` attribute holds the output."""
    def __init__(self, result: Any):
        self.result = result


class Failure(Result):
    """Indicates that the function failed. The `errors` attribute holds a list of discovered `Error`s."""
    def __init__(self, errors: list[Error]):
        self.errors = errors


class UnrecognizedWordError(Error):
    """Indicates that there were no appropriate matches for a given word, stored in `word`."""
    def __init__(self, word: str):
        self.word = word

# This class is also a little ambiguous
class AmbiguousWordError(Error):
    """
    Indicates that multiple matches were equally appropriate for a given word. Given word is stored in the `word`
    attribute, and the possible canonical representations are stored in the `options` attribute.
    """
    def __init__(self, word: str, options: list[str]):
        self.word = word
        self.options = options

# I'm sorry, what?
class UnclassifiedWordError(Error):
    """
    Indicates a mismatch between the Processor's `WordClassifier` and the underlying Identifier's `WordIndex`, as the
    WordIndex returned a canonical representation that was not classified. The offending word is stored in the `word`
    attribute.
    """
    def __init__(self, word: str):
        self.word = word


class NounPhrase:
    def __init__(self, noun: str, qualifiers=None):
        self._noun = noun
        self._prepositions = {}
        if qualifiers is None:
            self._qualifiers = []
        else:
            self._qualifiers = qualifiers

    @property
    def noun(self) -> str:
        return self._noun

    @property
    def prepositions(self) -> dict[str, list['NounPhrase']]:
        return self._prepositions

    @property
    def qualifiers(self) -> list[str]:
        return self._qualifiers

    def __contains__(self, item) -> bool:
        return item in self._prepositions

    def add_qualifier(self, qualifier: str):
        self._qualifiers.append(qualifier)

    def add_preposition(self, preposition: str, dependents: 'NounPhrase'):
        self._prepositions[preposition] = dependents


class PrepositionalPhrase:
    def __init__(self, preposition: str, dependents: list[NounPhrase]):
        self.preposition = preposition
        self.dependents = dependents


class Action:
    def __init__(self):
        self._verb = None
        self._direct_objects = []
        self._last_modified = []

    def has_verb(self) -> bool:
        return self._verb is not None

    def set_verb(self, verb: str):
        self._verb = verb

    @property
    def verb(self) -> str:
        return self._verb

    @property
    def direct_objects(self) -> list[NounPhrase]:
        return self._direct_objects

    def add_direct_object(self, direct_object: NounPhrase):
        self._direct_objects.append(direct_object)

    def add_prepositional_phrase(self, prepositional_phrase: PrepositionalPhrase):
        cached = self._last_modified
        self._last_modified = []
        for noun in self._direct_objects:
            if prepositional_phrase.preposition not in noun:
                self._last_modified.append(noun)
                noun.add_preposition(prepositional_phrase.preposition, prepositional_phrase.dependents)
        if len(self._last_modified) == 0:
            for noun in cached:
                x = noun.copy()
                self.add_direct_object(x)
                x.add_preposition(prepositional_phrase.preposition, prepositional_phrase.dependents)
                self._last_modified.append(noun)
            self._last_modified = cached

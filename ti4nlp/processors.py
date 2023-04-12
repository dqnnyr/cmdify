import abc
import re

from ti4nlp.lexica import WordClassifier
from ti4nlp.result import Result, Success, Failure, UnrecognizedWordError, AmbiguousWordError, UnclassifiedWordError
from ti4nlp.identifiers import Identifier


class NounPhrase:
    def __init__(self, noun: str, qualifiers=None):
        self._noun = noun
        self._prepositions = {}
        if qualifiers is None:
            self._qualifiers = []
        else:
            self._qualifiers = qualifiers

    @property
    def noun(self):
        return self._noun

    def __contains__(self, item):
        return item in self._prepositions

    def add_qualifier(self, qualifier: str):
        self._qualifiers.append(qualifier)

    def add_preposition(self, preposition: str, dependents):
        self._prepositions[preposition] = dependents

    def get_prepositions(self):
        return self._prepositions.items()


class PrepositionalPhrase:
    def __init__(self, preposition: str, dependents: list[NounPhrase]):
        self.preposition = preposition
        self.dependents = dependents


class Action:
    def __init__(self):
        self.verb = None
        self.direct_objects = []
        self.prepositional_phrases = []
        self._last_modified = []

    def has_verb(self) -> bool:
        return self.verb is not None

    def set_verb(self, verb: str):
        self.verb = verb

    def add_direct_object(self, direct_object: NounPhrase):
        self.direct_objects.append(direct_object)

    def add_prepositional_phrase(self, prepositional_phrase: PrepositionalPhrase):
        cached = self._last_modified
        self._last_modified = []
        for noun in self.direct_objects:
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


class QueryProcessor:
    __metaclass__ = abc.ABCMeta

    def __init__(self, word_classifier: WordClassifier, identifier: Identifier):
        self.word_classifier = word_classifier
        self.identifier = identifier

    @staticmethod
    def preprocess(query: str) -> list[str]:
        and_ified = re.sub(r'[,;/]+', ' and ', query)
        return [token for token in and_ified.split(' ') if len(token)]

    @abc.abstractmethod
    def process(self, query: str) -> Result:
        return Result()

    @abc.abstractmethod
    def interpret(self, tokens: list[str]):
        return


class SimpleQueryProcessor(QueryProcessor):
    def __init__(self, word_classifier: WordClassifier, identifier: Identifier, *,
                 noun_class: str = 'noun',
                 verb_class: str = 'verb',
                 qualifier_class: str = 'qualifier',
                 conjunction_class: str = 'conjunction',
                 preposition_class: str = 'preposition',
                 particle_class: str = 'particle'):
        super().__init__(word_classifier, identifier)
        self.noun_class = noun_class
        self.verb_class = verb_class
        self.qualifier_class = qualifier_class
        self.preposition_class = preposition_class
        self.conjunction_class = conjunction_class
        self.particle_class = particle_class

    def process(self, query: str):
        tokens = self.preprocess(query)
        canonical_words = self.identifier.find_best_from_all(tokens)

        errors = []
        for original, candidates in canonical_words:
            if len(candidates) > 1:
                errors.append(AmbiguousWordError(original, candidates))
            elif len(candidates) == 0:
                errors.append(UnrecognizedWordError(original))
            elif candidates[0] not in self.word_classifier:
                errors.append(UnclassifiedWordError(candidates[0]))
        if len(errors):
            return Failure(errors)

        return Success(self.interpret([item[1][0] for item in canonical_words]))

    def interpret(self, tokens: list[str]):
        actions = []

        action = Action()
        preposition = None
        qualifiers = []
        for token in tokens:
            if token in self.word_classifier[self.verb_class]:
                if action.has_verb():
                    actions.append(action)
                    action = Action()
                action.set_verb(token)
            elif token in self.word_classifier[self.preposition_class]:
                preposition = token
            elif token in self.word_classifier[self.noun_class]:
                np = NounPhrase(token, qualifiers)
                qualifiers = []
                if preposition is not None:
                    pp = PrepositionalPhrase(preposition, [np])
                    action.add_prepositional_phrase(pp)
                    preposition = None
                else:
                    action.add_direct_object(np)
            elif token in self.word_classifier[self.qualifier_class]:
                qualifiers.append(token)
        actions.append(action)

        return actions

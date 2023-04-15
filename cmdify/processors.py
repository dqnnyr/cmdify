import abc
import re

from cmdify.identifiers import Identifier
from cmdify.lexica import WordClassifier
from cmdify.result import *


class QueryProcessor:
    __metaclass__ = abc.ABCMeta

    def __init__(self, word_classifier: WordClassifier, identifier: Identifier):
        self.word_classifier = word_classifier
        self.identifier = identifier

    @staticmethod
    def preprocess(query: str) -> list[str]:
        tokens: list[str] = re.findall(r'[^"\s]\S*|".+?"', re.sub(r'[,;/]+', ' and ', query))
        return [token[1:-1].strip() if token[0] == '"' and token[0] == token[-1] else token for token in tokens]

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

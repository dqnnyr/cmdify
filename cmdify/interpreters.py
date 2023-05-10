import abc

from cmdify.identifiers import Identifier
from cmdify.lexica import WordClassifier
from cmdify.result import Result, Action, NounPhrase, PrepositionalPhrase

# Do we need this abstract class?
class Interpreter(abc.ABC):
    def __init__(self, word_classifier):
        self.word_classifier = word_classifier

    @abc.abstractmethod
    def interpret(self, tokens: list[str]) -> Result:
        return Result()


class SimpleInterpreter(Interpreter):
    def __init__(self, word_classifier: WordClassifier, *,
                 noun_class: str = 'noun',
                 verb_class: str = 'verb',
                 qualifier_class: str = 'qualifier',
                 conjunction_class: str = 'conjunction',
                 preposition_class: str = 'preposition',
                 particle_class: str = 'particle'):
        super().__init__(word_classifier)
        self.noun_class = noun_class
        self.verb_class = verb_class
        self.qualifier_class = qualifier_class
        self.preposition_class = preposition_class
        self.conjunction_class = conjunction_class
        self.particle_class = particle_class

    # I'm sorry, what?
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

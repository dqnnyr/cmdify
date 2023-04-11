import abc
import re

from ti4nlp.lexica import WordClassifier
from ti4nlp.result import Success, Failure, UnrecognizedWordError, AmbiguousWordError


class QueryProcessor:
    __metaclass__ = abc.ABCMeta

    def __init__(self, word_classifier: WordClassifier, identifier):
        self.word_classifier = word_classifier
        self.identifier = identifier

    @staticmethod
    def preprocess(query: str) -> list[str]:
        and_ified = re.sub(r'[,;/]+', ' and ', query)
        return [token for token in and_ified.split(' ') if len(token)]

    @abc.abstractmethod
    def process(self, query: str):
        return


class SimpleQueryProcessor(QueryProcessor):
    def __init__(self, word_classifier, identifier, *,
                 noun_class='noun',
                 verb_class='verb',
                 qualifier_class='qualifier',
                 conjunction_class='conjunction',
                 preposition_class='preposition'):
        self.noun_class = noun_class
        self.verb_class = verb_class
        self.qualifier_class = qualifier_class
        self.preposition_class = preposition_class
        self.conjunction_class = conjunction_class
        super().__init__(word_classifier, identifier)

    def process(self, query):
        tokens = self.preprocess(query)
        meanings_queue = self.identifier.find_best_from_all(tokens)

        # Potential return types
        actions = []
        errors = []

        # The action object to be built
        action = {'verb': None, 'objects': []}

        # Parameters for helping process groups of words.
        target = None
        more = False
        quality_prefix = ''

        for token, meanings in meanings_queue:
            # Once an error is encountered, we give up on actually processing,
            # since the actions will probably end up nonsense if we do.
            if len(meanings) != 1 or len(errors):
                if len(meanings) == 0:
                    errors.append(UnrecognizedWordError(token))
                elif len(meanings) > 1:
                    errors.append(AmbiguousWordError(token, meanings))
                continue
            true_meaning = meanings[0]

            if true_meaning in self.word_classifier[self.noun_class]:
                if more and target:
                    action[target].append(quality_prefix + true_meaning)
                else:
                    action['objects'].append(quality_prefix + true_meaning)
                more = False
                quality_prefix = ''

            elif true_meaning in self.word_classifier[self.verb_class]:
                # If there's an outstanding adjective, just treat it as a noun.
                if len(quality_prefix):
                    if target:
                        action[target].append(quality_prefix[:-1])
                    else:
                        action['objects'].append(quality_prefix[:-1])
                    quality_prefix = ''

                # Reset for the next action.
                target = None
                more = False
                if action['verb']:
                    actions.append(action)
                    action = {'verb': None, 'objects': []}
                action['verb'] = true_meaning

            elif true_meaning in self.word_classifier[self.preposition_class]:
                # With prepositions, we expect the next noun(s) to be
                # applying to the preposition, i.e., in "move to Paris",
                # "to Paris" indicates more than "move Paris"

                # If there's an outstanding adjective, just treat it as a noun.
                if len(quality_prefix):
                    if target:
                        action[target].append(quality_prefix[:-1])
                    else:
                        action['objects'].append(quality_prefix[:-1])
                    quality_prefix = ''
                # Setting up the preposition for assignment
                action[true_meaning] = []
                target = true_meaning
                more = True

            elif true_meaning in self.word_classifier[self.qualifier_class]:
                # Adjectives are appended before the next noun,
                # or in desperate times just treated as nouns.
                quality_prefix = quality_prefix + true_meaning + ' '
            elif true_meaning in self.word_classifier[self.conjunction_class]:
                more = True

        actions.append(action)
        return Failure(errors) if len(errors) else Success(actions)

from typing import Type, Any
from cmdify.preprocessors import Preprocessor
from cmdify.interpreters import Interpreter
from cmdify.identifiers import Identifier, IdentifierWrapper
from cmdify.result import Result, AmbiguousWordError, UnrecognizedWordError, UnclassifiedWordError, Failure, Success
from cmdify.lexica import generate_index_and_classifier


class QueryProcessorFactory:
    def __init__(self):
        self._vocabulary = {}

        self._preprocessor_params = {}
        self._preprocessor = None

        self._identifier_params = {}
        self._identifier = None
        self._identifier_wrappers = []

        self._interpreter_params = {}
        self._interpreter = None

    def set_vocabulary(self, **vocabulary: dict[str, list[str]]) -> 'QueryProcessorFactory':
        self._vocabulary = vocabulary
        return self

    def set_preprocessor(self, preprocessor_class: Type[Preprocessor], **params) -> 'QueryProcessorFactory':
        self._preprocessor = preprocessor_class
        self._preprocessor_params = params
        return self

    def set_identifier(self, identifier_class: Type[Identifier], **params) -> 'QueryProcessorFactory':
        self._identifier = identifier_class
        self._identifier_params = params
        return self

    def add_identifier_wrapper(self, wrapper_class: Type[IdentifierWrapper], **params) -> 'QueryProcessorFactory':
        self._identifier_wrappers.append((wrapper_class, params))
        return self

    def set_interpreter(self, interpreter_class: Type[Interpreter], **params) -> 'QueryProcessorFactory':
        self._interpreter = interpreter_class
        self._interpreter_params = params
        return self

    def build(self) -> 'QueryProcessor':
        index, classifier = generate_index_and_classifier(**self._vocabulary)
        preprocessor = self._preprocessor(**self._preprocessor_params)
        identifier = self._identifier(index, **self._identifier_params)

        for id_class, params in self._identifier_wrappers:
            identifier = id_class(identifier, **params)

        interpreter = self._interpreter(classifier, **self._interpreter_params)
        return QueryProcessor(preprocessor, identifier, interpreter)


class QueryProcessor:
    def __init__(self, preprocessor: Preprocessor, identifier: Identifier, interpreter: Interpreter):
        self._preprocessor = preprocessor
        self._identifier = identifier
        self._interpreter = interpreter

    @staticmethod
    def factory():
        return QueryProcessorFactory()

    # Processes original query and either returns an error or calls the interpreter
    def process(self, query) -> Result:
        # Split query into tokens
        tokens = self._preprocessor.preprocess(query)
        # Convert tokens into similar recognized words or 
        # Again, canonical
        canonical_words = self._identifier.identify_all(tokens)

        errors = []
        for original, candidates in canonical_words:
            if len(candidates) > 1: # Original word is ambiguous --> in what way?
                errors.append(AmbiguousWordError(original, candidates))
            elif len(candidates) == 0: # Original word does not have a similar word in the vocabulary --> wdtm?
                errors.append(UnrecognizedWordError(original))
            elif candidates[0] not in self._interpreter.word_classifier: # Candidate word not in classifier --> so not in the vocabulary at all?
                errors.append(UnclassifiedWordError(candidates[0]))
        if len(errors):
            return Failure(errors)

        # Interpret canonical words and return result as Success --> what is success?
        return Success(self._interpreter.interpret([item[1][0] for item in canonical_words]))
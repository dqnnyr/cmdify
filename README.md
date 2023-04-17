# cmdify

A lightweight command-line language processing tool, originally developed for Twilight Imperium 4.

## Installation

```commandline
pip install cmdify
```

## Usage

```python
from cmdify.core import QueryProcessor
from cmdify.preprocessors import SimplePreprocessor
from cmdify.identifiers import GraphPruningIdentifier, CachedIdentifier
from cmdify.interpreters import SimpleInterpreter
from cmdify.result import *

vocabulary = {
    'noun': {
        'dog': ['wolf'],
        'fox': [],
    },
    'qualifier': {
        'quick': ['fast', 'brisk'],
        'brown': [],
        'lazy': [],
    },
    'verb': {
        'play': [],
        'jump': ['leap', 'hop'],
    },
    'preposition': {
        'over': ['above'],
        'under': ['below'],
        'to': ['towards']
    },
    'conjunction': {
        'and': []
    },
    'skip_word': {
        'a': ['an'],
        'the': []
    },
}

processor = QueryProcessor.factory()\
    .set_vocabulary(**vocabulary)\
    .set_preprocessor(SimplePreprocessor)\
    .set_identifier(GraphPruningIdentifier, threshold=6)\
    .add_identifier_wrapper(CachedIdentifier, buffer_size=60)\
    .set_interpreter(SimpleInterpreter)\
    .build()

result = processor.process('leap over the lazy dog')

if isinstance(result, Success):
    actions: list[Action] = result.result
    # Some sort of processing . . .
elif isinstance(result, Failure):
    errors: list[Error] = result.errors
    # Some sort of processing . . .
```
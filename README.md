## Installation

Will be available with Release-0.1.

## Usage

```python
from cmdify.lexica import generate_index_and_classifier
from cmdify.identifiers import GraphPruningIdentifier, CachedIdentifier
from cmdify.processors import SimpleQueryProcessor
from cmdify.result import Success, Failure, AmbiguousWordError, UnrecognizedWordError

vocabulary = {
    'noun': {
        'card': ['spell'], 'tableau': ['board'], 'hand': [], 'player': [],
        'Fireball': [], 'Lightning': [], 'Bubble Beam': [],
    },
    'qualifier': {
        'fast': ['quick'], 'slow': [],
        'red': [], 'yellow': [], 'blue': [], 'green': [],
    },
    'verb': {'play': ['cast'], 'discard': ['forget'], 'gain': ['learn']},
    'preposition': {'to': ['on']},
    'conjunction': {'and': []},
    'skip_word': {'a': ['an'], 'the': []},
}

synonym_index, classifier = generate_index_and_classifier(**vocabulary)

gpi = GraphPruningIdentifier(synonym_index, threshold=6)
word_identifier = CachedIdentifier(gpi, buffer_size=10)

processor = SimpleQueryProcessor(classifier, word_identifier)

# The GraphPruningIdentifier utilizes fuzzy detection.
output = processor.process('play fireblal on the blue player and discard Lightning')

if isinstance(output, Success):
    for action in output.result:
        print(action)
elif isinstance(output, Failure):
    for error in output.errors:
        if isinstance(error, AmbiguousWordError):
            print(f'Ambiguous word "{error.word}" (could be: {", ".join(error.options)})')
        elif isinstance(error, UnrecognizedWordError):
            print(f'Unrecognized word "{error.word}"')
```

Expected output:
```
{'verb': 'play', 'components': ['Fireball'], 'on': ['blue player']}
{'verb': 'discard', 'components': ['Lightning']}
```
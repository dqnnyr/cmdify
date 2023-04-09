## Installation

Will be available with Release-0.1.

## Usage

```python
from ti4nlp.lexica import generate_index_and_classifier
from ti4nlp.identifiers import GraphPruningIdentifier
from ti4nlp.processors import SimpleQueryProcessor
from ti4nlp.result import Success, Failure, AmbiguousWordError, UnrecognizedWordError

data = {
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

index, classifier = generate_index_and_classifier(**data)

identifier = GraphPruningIdentifier(index, threshold=6)
processor = SimpleQueryProcessor(classifier, identifier)

output = processor.process('play Fireball on the blue player')

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
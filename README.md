## Installation

Will be available with Release-0.1.

## Usage

```python
from cmdify.lexica import generate_index_and_classifier
from cmdify.identifiers import GraphPruningIdentifier, CachedIdentifier
from cmdify.processors import SimpleQueryProcessor
from cmdify.result import *

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
    results: list[Action] = output.result

    for action in results:
        print(f'Action: {action.verb}')
        for noun in action.direct_objects:
            if len(noun.qualifiers):
                print(f'    {noun.noun} ({", ".join(noun.qualifiers)})')
            else:
                print(f'    {noun.noun}')
            prepositions: dict[str, list[NounPhrase]] = noun.prepositions
            for prep, deps in noun.prepositions.items():
                objects_of_preposition = [f'{n.noun} ({n.qualifiers})' if len(n.qualifiers) else f'{n.noun}' for n in deps]
                print(f'        {prep}: {", ".join(objects_of_preposition)}')

elif isinstance(output, Failure):
    errors: list[Error] = output.errors

    for error in errors:
        if isinstance(error, UnrecognizedWordError):
            # If the fuzzy detection found no close matches, or the literal detection
            # produced no results, an `UnrecognizedWordError` is returned.
            print(f'Unrecognized word "{error.word}"')
        elif isinstance(error, AmbiguousWordError):
            # If the fuzzy detection returned multiple possible words with equal weight,
            # an `AmbiguousWordError` is returned.
            print(f'Ambiguous word "{error.word}" (could be: {", ".join(error.options)})')
        elif isinstance(error, UnclassifiedWordError):
            # This represents a desync between the WordClassifier and SynonymIndex.
            # Cannot occur when using `generate_index_and_classifier`.
            print(f'The word "{error.word}" could not be classified!')
```

Expected output:
```
Action: play
    Fireball
        on: player (blue)
Action: discard
    Lightning
```
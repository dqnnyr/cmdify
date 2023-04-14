## Installation

Will be available with Release-0.1.

## Usage

```python
# Why do we not have a main function with this in it?
from ti4nlp.lexica import generate_index_and_classifier
from ti4nlp.identifiers import GraphPruningIdentifier
from ti4nlp.processors import SimpleQueryProcessor
from ti4nlp.result import Success, Failure, AmbiguousWordError, UnrecognizedWordError

# This is the vocabulary that is used to classify words
# It's a dictionary, but why do some keys have blank lists? 
# Ex: Lightning
# Would players be added to the data during the game? 
# Why is it formatted like this? 

# To answer my own questions, this is a list of terms (classified by parts of speech)
# Each key is a general word, with the values being any synonyms that a user might type instead
# Example: in this data, the only type of card is a spell. 
# A player could "play a card" or "play a spell" and both would have the same result
# this should probably be called "terms" or "vocabulary" because "data" is too vague
data = {
    # parts of speech
    'noun': {
        # general nouns followed by the "types" that relate to each word
        # the one that really throws me off is spell and card. 
        # The list format makes it seem like several types of cards could be played
        # I understand now what the main idea is, but I think more documentation is needed/better comments
        # Most of this is not "intutive" if you don't already know what's going on
        'card': ['spell'], 'tableau': ['board'], 'hand': [], 'player': [],
        'Fireball': [], 'Lightning': [], 'Bubble Beam': [],
    },
    'qualifier': {
        # here it makes sense because 'quick' actually is an alias of fast
        'fast': ['quick'], 'slow': [],
        'red': [], 'yellow': [], 'blue': [], 'green': [],
    },
    'verb': {'play': ['cast'], 'discard': ['forget'], 'gain': ['learn']},
    'preposition': {'to': ['on']},
    'conjunction': {'and': []},
    'skip_word': {'a': ['an'], 'the': []},
}

# See lexica.py (creates the index and the classifier)
# Also why **data?
# index is too broad of a term
# classifier kinda makes sense
index, classifier = generate_index_and_classifier(**data)

# See identifiers.py (uses the index to remove irrelevant words?)
# identifier might also be too vague
identifier = GraphPruningIdentifier(index, threshold=6)

# See processors.py (processes the query)
# takes in the classifier and identifier in order to actually process the query
processor = SimpleQueryProcessor(classifier, identifier)

# The GraphPruningIdentifier utilizes fuzzy detection.
# Reads query, returns results
output = processor.process('play fireblal on the blue player and discard Lightning')

# Is success a function? Where does it come from? Why is it being imported instead of set as a value?
if isinstance(output, Success):
    for action in output.result:
        print(action)
elif isinstance(output, Failure):
    for error in output.errors:
        if isinstance(error, AmbiguousWordError):
            print(f'Ambiguous word "{error.word}" (could be: {", ".join(error.options)})')
        elif isinstance(error, UnrecognizedWordError):
            print(f'Unrecognized word "{error.word}"')
# What happens if somehow neither of these cases happen? Why is it set up as an elif instead of else?
```

Expected output:
```
{'verb': 'play', 'components': ['Fireball'], 'on': ['blue player']}
{'verb': 'discard', 'components': ['Lightning']}
```
So what do we do with the output?
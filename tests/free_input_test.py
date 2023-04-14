from ti4nlp.lexica import generate_index_and_classifier
from ti4nlp.identifiers import GraphPruningIdentifier
from ti4nlp.processors import SimpleQueryProcessor
from ti4nlp.result import Success, Failure, AmbiguousWordError, UnrecognizedWordError
from lexica_tests import get_test_data


def test():
    data = get_test_data()
    index, classifier = generate_index_and_classifier(**data)

    identifier = GraphPruningIdentifier(index, threshold=6)
    processor = SimpleQueryProcessor(classifier, identifier)
    # The SimpleQueryProcessor utilizes fuzzy detection.
    query = input('Query: ')
    while query != 'quit':
        output = processor.process(query)

        if isinstance(output, Success):
            for action in output.result:
                print(f'Action: {action.verb}')
                for noun in action.direct_objects:
                    qualifiers = f' ({", ".join(noun._qualifiers)})' if len(noun._qualifiers) else ''
                    print(f'    {noun.noun}{qualifiers}')
                    for prep, deps in noun._prepositions.items():
                        deps_list = [f'{n.noun} ({n._qualifiers})' if len(n._qualifiers) else f'{n.noun}' for n in deps]
                        print(f'        {prep}: {", ".join(deps_list)}')
        elif isinstance(output, Failure):
            for error in output.errors:
                if isinstance(error, AmbiguousWordError):
                    print(f'Ambiguous word "{error.word}" (could be: {", ".join(error.options)})')
                elif isinstance(error, UnrecognizedWordError):
                    print(f'Unrecognized word "{error.word}"')
        query = input('Query: ')


if __name__ == '__main__':
    test()
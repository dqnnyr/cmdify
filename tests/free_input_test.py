from cmdify.core import QueryProcessor
from cmdify.lexica import generate_index_and_classifier
from cmdify.identifiers import GraphPruningIdentifier, CachedIdentifier
from cmdify.interpreters import SimpleInterpreter
from cmdify.preprocessors import SimplePreprocessor
from cmdify.result import Success, Failure, Error, AmbiguousWordError, UnrecognizedWordError, Action, NounPhrase
import itertools


def get_test_data():
    return {
        'noun': {
            'Infantry': ['inf', 'i', 'spec ops', 'letani warrior', 'letani', 'crimson legionnaire'],
            'Ground Force': ['gf'],
            'Mech': ['letani behemoth', 'aerie sentinel', 'dunlain reaper', 'scavenger zeta', 'ember colossus',
                     'pride of kenara', 'watcher', 'zs thunderbolt m2', 'icarus drive', 'annihilator', 'starlancer',
                     'moll terminus', 'iconoclast', 'eidolon', 'z-grav eidolon', 'mordred', 'quantum manipulator',
                     'valkyrie exoskeleton', 'hecatoncheries', 'shield paling', 'reanimator', 'reclaimer', 'indomitus',
                     "moyin's ashes", 'blackshade infiltrator'],
            'Fighter': ['ff', 'hybrid crystal fighter', 'crystal fighter', 'hcf', 'cf'],
            'Dreadnought': ['dread', 'super dreadnought', 'sdread', 'super dread', 'exotrireme'],
            'Destroyer': ['dest', 'dd', 'strike wing alpha', 'swa', 'swing alpha', 'swing'],
            'Cruiser': ['saturn engine', 'saturn'],
            'Carrier': ['advanced carrier', 'adv carrier'],
            'Flagship': ['duha menaimon', 'quetzecoatl', 'arc secundus', 'son of ragh', 'artemiris', 'the inferno',
                         'wrath of kenara', 'dynamo', 'genesis', 'hil colish', '[0.0.1]', 'arvicon rex', 'fourth moon',
                         'matriarch', 'visz el vir', 'the alastor', 'memoria', "c'morran n'orr", 'ouranos',
                         'j.n.s. hylarim', 'the terror between', 'salai sai corian', 'loncarra ssodu', 'van hauge',
                         "y'sia y'ssarila"],
            'War Sun': ['ws', 'prototype war sun', 'proto war sun', 'pws'],
            'PDS': ['Planetary Defense System', 'hel titan'],
            'Space Dock': ['sd', 'dock', 'floating factory', 'dimensional tear'],
            'Mecatol Rex': ['mr', 'mecrex', 'mec rex'],
            'planet': [],
            'Lirta IV': ['lirta4', 'lirta 4'],
            'Vefut II': ['vefut2'],
            'Rigel I': ['rigel1'],
            'Rigel II': ['rigel2'],
            'Rigel III': ['rigel3'],
            'Mordai II': ['mordai2'],
            **{k: [] for k in [
                'Nestphar', 'Arc Prime', 'Wren Terra', 'Lisis II', 'Ragh', 'Muaat', 'Hercant', 'Arretze', 'Kamdorn',
                'Jord', 'Creuss', '[0.0.0]', 'Moll Primus', 'Druaa', 'Maaluuk', "Tren'Lak", 'Quinarra', 'Jol', 'Nar',
                'Winnu', 'Archon Ren', 'Archon Tau', 'Darien', 'Retillion', 'Shalloq', 'Valk', 'Avar', 'Ylir',
                'The Dark', 'Ixth', 'Naazir', 'Rokha', 'Arcturus', 'Elysium', 'Acheron',
                'Abyz', 'Fria', 'Arinam', 'Meer', 'Arnor', 'Lor', 'Bereg', 'Centauri', 'Gral', 'Coorneeq',
                'Resculon', 'Dal Bootha', 'Xxehan', 'Lazar', 'Sakulag', 'Lodor', 'Mehar Xull', 'Mellon', 'Zohbat',
                'New Albion', 'Starpoint', 'Quann', "Qucen'n", 'Rarron', 'Saudor', "Tar'mann", "Tequ'ran", 'Torkan',
                'Thibah', 'Wellon', 'Archon Vail', 'Perimeter', 'Ang', 'Sem-Lore', 'Vorhal', 'Atlas', 'Primor',
                "Hope's End", 'Cormund', 'Everra', 'Jeol Ir', 'Accoen', 'Kraag', 'Siig', "Ba'kal", 'Alio Prima',
                'Lisis', 'Velnor', 'Cealdri', 'Xanhact', 'Vega Major', 'Vega Minor', 'Abaddon', 'Ashtroth', 'Loki',
                'Mallice', 'Mirage',
                *[a + 'a' for a in ['0', '1', '2', '3', '4']],
                *[a + b for a, b in itertools.product(['1', '2', '3', '4'], ['b', 'c', 'd', 'e', 'f'])],
                *[a + b for a, b in itertools.product(['2', '3', '4'], ['g', 'h', 'i', 'j', 'k', 'l'])],
                *[a + b for a, b in itertools.product(['3', '4'], ['m', 'n', 'o', 'p', 'q', 'r'])],
                *[a + b for a, b in itertools.product(['4'], ['s', 't', 'v', 'w', 'x', 'z'])],
            ]},
        },
        'verb': {
            'activate': [],
            'add': ['place'],
            'remove': ['destroy'],
            'move': [],
        },
        'qualifier': {
            '0': ['zero', 'no'],
            '1': ['one'],
            '2': ['two', 'couple'],
            '3': ['three'],
            '4': ['four'],
            '5': ['five'],
            '6': ['six', 'half dozen', 'half-dozen'],
            '7': ['seven'],
            '8': ['eight'],
            '9': ['nine'],
            '10': ['ten'],
            '11': ['eleven'],
            '12': ['twelve', 'dozen'],
            'each': ['every', 'any', 'all'],
            'damaged': ['sustained'],
            'exhausted': ['flipped'],
        },
        'conjunction': {
            'and': [],
            'then': [],
        },
        'preposition': {
            'to': ['onto'],
            'in': ['on'],
            'from': [],
            'with': ['for', 'as'],
        },
        'skip_word': {
            'a': ['an'],
            'the': [],
        },
    }


def test():
    processor = QueryProcessor.factory()\
        .set_vocabulary(**get_test_data())\
        .set_preprocessor(SimplePreprocessor)\
        .set_identifier(GraphPruningIdentifier, threshold=6)\
        .add_identifier_wrapper(CachedIdentifier, buffer_size=60)\
        .set_interpreter(SimpleInterpreter)\
        .build()

    # The SimpleQueryProcessor utilizes fuzzy detection.
    query = input('Query: ')
    while query != 'quit':
        output = processor.process(query)

        if isinstance(output, Success):
            results: list[Action] = output.result

            for action in results:
                print(f'Action: {action._verb}')
                direct_objects: list[NounPhrase] = action.direct_objects
                for noun in direct_objects:
                    qualifiers = f' ({", ".join(noun.qualifiers)})' if len(noun.qualifiers) else ''
                    print(f'    {noun.noun}{qualifiers}')
                    for prep, deps in noun.prepositions.items():
                        deps_list = [f'{n.noun} ({n.qualifiers})' if len(n.qualifiers) else f'{n.noun}' for n in deps]
                        print(f'        {prep}: {", ".join(deps_list)}')
        elif isinstance(output, Failure):
            errors: list[Error] = output.errors

            for error in errors:
                if isinstance(error, AmbiguousWordError):
                    print(f'Ambiguous word "{error.word}" (could be: {", ".join(error.options)})')
                elif isinstance(error, UnrecognizedWordError):
                    print(f'Unrecognized word "{error.word}"')
        query = input('\nQuery: ')


if __name__ == '__main__':
    test()

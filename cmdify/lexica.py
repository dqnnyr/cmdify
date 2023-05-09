class SynonymReverseIndex:
    """
    Constructs a reverse index for the purposes of getting a 'canonical representation' of words.

    .. highlight:: python
    .. code-block:: python
        sri = SynonymReverseIndex(**{'term1': ['synonym1', 'synonym2'], 'term2': ['synonym3'], 'term3': []})
        assert sri['synonym2'] == 'term1'
        assert sri['term2'] == 'term2'
    """

    def __init__(self, **all_words):
        self._synonym_index = {}
        for primary_term, synonyms in all_words.items():
            self._add_to_index(primary_term, synonyms)

    def _add_to_index(self, primary_term: str, synonyms: list[str]):
        lowercase = primary_term.lower()
        if lowercase in self._synonym_index:
            value = self._synonym_index[lowercase]
        else:
            value = primary_term
            self._synonym_index[lowercase] = value
        for alias in synonyms:
            self._synonym_index[alias.lower()] = value

    def __getitem__(self, item: str) -> str:
        """
        Given a word, returns the canonical representation; if there is none, throws an exception.
        :param item: the synonym to consider
        :return: canonical representation of the word
        """
        return self._synonym_index[item]

    def __contains__(self, item: str) -> bool:
        """
        Given a word, returns whether that word is recognized by the dictionary.
        :param item: the word to consider
        :return: whether this index recognizes that word
        """
        return item in self._synonym_index

    def items(self):
        return self._synonym_index.items()

    def keys(self):
        return self._synonym_index.keys()

    def values(self):
        return self._synonym_index.values()


class WordClassifier:
    """
    .. highlight:: python
    .. code-block:: python
        wc = WordClassifier({'noun': ['apple', 'orange'], 'verb': ['eat']})
        assert 'apple' in wc['noun']
        assert 'eat' in wc['verb']
    """
    def __init__(self, **classifications_and_words):
        self._data = {}
        for classification, words in classifications_and_words.items():
            self._data[classification] = set(words)

    def __getattr__(self, attr):
        return self._data[attr]

    def __getitem__(self, item: str) -> set[str]:
        return self._data[item]

    def __contains__(self, item: str) -> bool:
        for key in self._data.keys():
            if item in self._data[key]:
                return True
        return False

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()


def generate_index_and_classifier(**class_words_and_synonyms: dict[str, list[str]]) -> \
        tuple[SynonymReverseIndex, WordClassifier]:
    classifications = {k: list(v.keys()) for k, v in class_words_and_synonyms.items()}
    term_synonyms = {}
    for synonym_dict in class_words_and_synonyms.values():
        for term, synonyms in synonym_dict.items():
            term_synonyms[term] = synonyms

    index = SynonymReverseIndex(**term_synonyms)
    classifier = WordClassifier(**classifications)
    return index, classifier

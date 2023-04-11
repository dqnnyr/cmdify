class WordIndex:
    def __init__(self, **words_and_aliases: list[str]):
        self._alias_index = {}
        for key_term, aliases in words_and_aliases.items():
            self._register(key_term, aliases)

    def _register(self, term: str, aliases: list[str]):
        lowered_term = term.lower()
        if lowered_term in self._alias_index:
            keyword = self._alias_index[lowered_term]
        else:
            keyword = term
            self._alias_index[lowered_term] = keyword
        for alias in aliases:
            self._alias_index[alias.lower()] = keyword

    def __getitem__(self, item: str) -> str:
        return self._alias_index[item]

    def __contains__(self, item: str) -> bool:
        return item in self._alias_index

    def items(self):
        return self._alias_index.items()

    def keys(self):
        return self._alias_index.keys()

    def values(self):
        return self._alias_index.values()


class WordClassifier:
    def __init__(self, **classes_and_words: dict[str, list[str]]):
        self._data = {}
        for clazz, words in classes_and_words.items():
            self._data[clazz] = set(words)

    def __getattr__(self, attr: str) -> set[str]:
        return self._data[attr]

    def __getitem__(self, item: str) -> set[str]:
        return self._data[item]

    def __contains__(self, item: str) -> bool:
        return item in self._data

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()


def generate_index_and_classifier(**class_words_and_aliases: dict[str, list[str]]) -> tuple[WordIndex, WordClassifier]:
    classifications = {k: list(v.keys()) for k, v in class_words_and_aliases.items()}
    term_aliases = {}
    for alias_dict in class_words_and_aliases.values():
        for term, aliases in alias_dict.items():
            term_aliases[term] = aliases
    index = WordIndex(**term_aliases)
    classifier = WordClassifier(**classifications)
    return index, classifier

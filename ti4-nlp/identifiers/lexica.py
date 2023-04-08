class WordIndex:
    def __init__(self, **words_and_aliases):
        self.alias_index = {}
        for key_term, aliases in words_and_aliases:
            self._register(key_term, aliases)

    pass

    def _register(self, term, aliases):
        lowered_term = term.lower()
        if lowered_term in self.alias_index:
            keyword = self.alias_index[lowered_term]
        else:
            keyword = term
            self.alias_index[lowered_term] = keyword
        for alias in aliases:
            self.alias_index[alias.lower()] = keyword


class WordClassifier:
    def __init__(self, **classes_and_words):
        self.data = {}
        for clazz, words in classes_and_words.items():
            self.data[clazz] = set(words)

    def __getattr__(self, attr):
        return self.data[attr]

    def __getitem__(self, item):
        return self.data[item]


def generate_index_and_classifier(**class_words_and_aliases):
    classifications = {k: list(v.keys()) for k, v in class_words_and_aliases.items()}
    aliases = {}
    for alias_dict in class_words_and_aliases.values():
        for term, aliases in alias_dict.items():
            aliases[term] = aliases
    index = WordIndex(**aliases)
    classifier = WordClassifier(**classifications)
    return index, classifier

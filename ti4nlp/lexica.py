# So I kept both because idk what changes you made and I didn't wanna fuck with shit
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

### END OF YOUR STUFF BEGINNING OF MINE ###
# tastes really good, but a little dry, could use some more comments

class SynonymIndex:
    def __init__(self, **all_words):
        self.synonym_index = {}
        for primary_term, synonyms in all_words.items():
            self._add_to_index(primary_term, synonyms)

    def _add_to_index(self, primary_term: str, synonyms: list[str]):
        #"what this function does" --> redudant and needs to be removed
        """
        Ex: {'work': ['act', 'do', 'labor']} 
        primary_term = 'work'
        synonyms = ['act', 'do', 'labor']
        This basically reverses the dictionary. 
        The keys are 'act', 'do', and 'labor', all with the value 'work'. 
        If the query has any synonyms, they all "translate" to the same word: 'work'. 
        """
        lowercase = primary_term.lower()
        # if the term is already a key in the dictionary, keyword = value of term
        if lowercase in self.synonym_index:
            value = self.synonym_index[lowercase]
        else:
            # perserves casing of the "original" word
            value = primary_term
            # add term to dict using lowercase as key
            # Ex: 'tomato': 'Tomato'
            self.synonym_index[lowercase] = value
        for alias in synonyms:
            # for each synonym, add the keyword as the value
            # Ex: 'ketchup' : 'Tomato', 'marinara': 'Tomato'
            # Would be formatted in data as 'Tomato' : ['ketchup', 'marinara']
            self.synonym_index[alias.lower()] = value


class WordClassifier:
    def __init__(self, **classes_and_words):
        self.data = {}
        # the fuck is a clazz. Daniel. What is this name Daniel. 
        # Daniel. I googled it. This is a Java convention. Daniel. This is python. The file is named lexia.py. 
        # What are you doing Daniel. 
        for clazz, words in classes_and_words.items():
            # what is a "class" of word? 
            # part of speech = keys of part of speech
            self.data[clazz] = set(words)

    # get 
    def __getattr__(self, attr):
        return self.data[attr]

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
# I did keep this one line from your stuff though
# I got rid of the other one
def generate_index_and_classifier(**class_words_and_aliases: dict[str, list[str]]) -> tuple[WordIndex, WordClassifier]:
    # The rest of this should be my stuff
    # makes a dictionary with k = part of speech, and then the keys are made into a list
    classifications = {k: list(v.keys()) for k, v in class_words_and_aliases.items()}
    term_aliases = {}
    # class_words_aliases = {greeting: {hi: [hello], sup: []}, farewell: {goodbye:[]}}
    # alias_dict = {hi: [hello]} (for the first iteration)
    # Combine all parts of speech dictionaries
    for alias_dict in class_words_and_aliases.values():
        # term = hi
        # alias = hello
        for term, aliases in alias_dict.items():
            # term_aliases = {hi: [hello]}
            term_aliases[term] = aliases
    # maps synonyms to true word
    index = WordIndex(**term_aliases)
    # identifies parts of speech
    classifier = WordClassifier(**classifications)
    return index, classifier

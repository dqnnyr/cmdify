import abc
from bidict import bidict
from cmdify.lexica import SynonymReverseIndex
from textdistance import damerau_levenshtein

# Parent class, useless as-is, but good basis for everything else
class Identifier(abc.ABC):
    def __init__(self, word_index: SynonymReverseIndex, threshold: int):
        self.word_index = word_index
        # What's the threshold for?
        self.threshold = threshold

    # This currently does nothing. Look at other Identifiers for implementation. 
    @abc.abstractmethod 
    def identify(self, tokens: str) -> tuple[list[str], int]:
        return [], self.threshold


    def identify_all(self, tokens: list[str]) -> list[tuple[str, list[str]]]:
        # makes tokens all lowercase
        tokens = [token.lower() for token in tokens]
        all_results = []
        # What is debt? -- Have not completely figured out
        debt = 0

        for index, token in enumerate(tokens):
            # Daniel's comment:
            # When we choose to hoard multiple tokens, we use this to skip them
            # when they should be investigated otherwise. Ends up behaving as a 
            # greedy algorithm, for better and for worse.
            if debt > 0:
                debt = debt - 1
                continue
            # sets the best_token to the current token
            best_token = token
            # NOTE: cmd_wrd is "command_word" --> the word actually used for the bot commands
            # Literal: best = (cmd_wrd, 0)
            best = self.identify(token)
            i = 1
            # sets new_token to current token
            new_token = token
            contender = ([], 0)
            # Loop runs until i is not 1 AND length of the contender is 0
            # OR 
            # the current index (so skipping all the words before it) + the number of words we've added so far 
            # is greater than the length of the overall list of tokens
            # TODO: Fix this --> Run through all possible, then just go from there (remove len(con))
            while (index + i < len(tokens)):
                # adding the next word in tokens
                new_token = new_token + ' ' + tokens[index + i]
                # Literal: sets contender to ([], threshold)
                contender = self.identify(new_token)
                # Literal: contender[1] is always threshold, so the if statement is skipped and the loop ends
                if contender[1] <= best[1]:
                    best = contender
                    best_token = new_token
                    debt = i
                i = i + 1

            results = []
            # this may not be needed? 
            if best[0] is not None:
                # adds any token in best that was not previously added
                [results.append(item) for item in best[0] if item not in results]
            # Literal: (cmd_wrd, [cmd_wrd])
            all_results.append((best_token, results))
        return all_results

# I am a little stupid. I do not see the point of this. Oh. Yes I do. Wack. 
class IdentifierWrapper(Identifier, abc.ABC):
    def __init__(self, identifier: Identifier):
        super().__init__(identifier.word_index, identifier.threshold)
        self._identifier = identifier

# Returns the "cannonical key" --> the word actually used in the command
# and a threshold of 0 every time
class LiteralIdentifier(Identifier):
    def identify(self, token: str) -> tuple[list[str], int]:
        # this is used to check for typos 
        # if the word is misstyped, then an empty list is returned
        if token in self.word_index:
            return [self.word_index[token]], 0
        return [], self.threshold


class FuzzyIdentifier(Identifier):

    # search word: bear
    # distance 1: [beer, fear, beat]

    def identify(self, token: str) -> tuple[list[str], int]:
        # pssd_wrd = token
        # reminder: the threshold is how many mistakes we're okay with the user making 
        # this is used to check for typos
        if token in self.word_index:
            return [self.word_index[token]], 0
        # creates tuple of empty list with threshold
        best = ([], self.threshold)
        # word = synonym (syn), keyword = command word (cmd_wrd)
        # iterates through all keys and values in word_index
        for word, keyword in self.word_index.items():
            # skips to next iteration if length btwn sysn and pssed_wrd > threshold + 1
            # If the diff in # of letters is too big we skip the word because what's the point
            # Ex: apple and applesauce are at least 5 apart
            if abs(len(word) - len(token)) > best[1] + 1:
                continue
            # calculates the distance between syn and pssd_wrd
            distance = damerau_levenshtein(token, word)
            # singular list with the cmd_wrd
            candidate = [keyword]
            # if dist btwn syn and pssd_wrd < threshold
            if distance < best[1]:
                # the new best is now [cmd_wrd] and dist
                best = (candidate, distance)
            # if dist is the same
            elif distance == best[1]:
                # add the list of candidates to candidate (there may be other words with similar distances)
                candidate.extend(best[0])
                # best is now the full list of candidates that closely match, best dist
                best = (candidate, distance)
        return best


class GraphPruningIdentifier(Identifier):
    def __init__(self, word_index: SynonymReverseIndex, threshold: int):
        super().__init__(word_index, threshold)
        self._graph = {}
        self._populate_graph()

    # this is a word dag (kinda but not really) 
    def _populate_graph(self):
        # gets all the words possible
        words = list(self.word_index.keys())
        # iterates through all possible words
        for word in words:
            # every word gets assigned a dict where keys are 1-threshold-1 and values are empty sets (they are updated later)
            self._graph[word] = {x: set() for x in range(1, self.threshold)}
        # i = index of word in words
        # a = first word
        # b = second word (skip the first word)
        # iterates through all the words from a given point onwards for all words in words
        for i, a in enumerate(words):
            for b in words[i+1:]:
                # calc dist btwn first word and second word
                distance = damerau_levenshtein(a, b)
                # if the dist < threshold
                if distance < self.threshold:
                    # we add b to a's set (where the key is the threshold)
                    self._graph[a][distance].add(b)
                    # we add a to b's set (where the key is the threshold)
                    self._graph[b][distance].add(a)

    def identify(self, token: str) -> tuple[list[str], int]:
        # if the passed in word (pssd_wrd) is already in the index, return the list containing just that and the threshold 0 
        # Exact match!
        if token in self.word_index:
            return [self.word_index[token]], 0
        # create a set of all the possible words from word_index 
        eligible_words = set(self.word_index.keys())
        # best is an empty list and the default threshold 
        best = ([], self.threshold)
        # word = synonym (syn), keyword = command word (cmd_wrd)
        # iterates through all keys and values in word_index
        for word, keyword in self.word_index.items():
            # if dist between syn and pssd_wrd is greater than 1 + threshold
            # or if word isn't in the index --> why does this exist? (removed from eligble_words because it was too close to words that were identified as too far away)
            # skip to the next iteration 
            if abs(len(word) - len(token)) > best[1] + 1 \
                    or word not in eligible_words:
                continue
            # damerau levenshtein dist btwn syn and pssd_wrd
            distance = damerau_levenshtein(token, word)
            # cand is list with cmd_wrd
            candidate = [keyword]
            # if dist < threshold
            if distance < best[1]:
                # the new best is ([cmd_wrd], dist)
                best = (candidate, distance)
            # otherwise, if dist = threshold
            elif distance == best[1]:
                # cand = cand + list of best words
                candidate.extend(best[0])
                # best is now the full list of cand, dist
                best = (candidate, distance)
            else:
                # Prune all words that definitely cannot beat the best, according to the graph
                # for every # between 1 and the threshold 
                for i in range(1, self.threshold):
                    # if the diff btwn dist and i > threshold
                    if distance - i > best[1]:
                        # no idea what this is doing here (assuming this is the prune part though)
                        # goes into the dict for word and then removes all with > dist than best dist
                        for irrelevant_word in self._graph[word][i]:
                            eligible_words.discard(irrelevant_word)
                    else:
                        break
        return best

# "This is bad" - Daniel, 2023
class CachedIdentifier(IdentifierWrapper):
    def __init__(self, identifier: Identifier, buffer_size: int):
        super().__init__(identifier) # feed it another identifier to identify the first time
        # this class is an imposter 
        # it just keeps track of the work another identifier has done but puts its name on it like a little shit
        assert buffer_size >= 0
        self._buffer_size = buffer_size # how many things go in the cache
        self._current_age = 0 # keeps track of what the most recent # is
        self._prune_age = 0 # keeps track of what needs to be gotten rid of first (FIFO)
        self._cache = {} # stores result of each query (up to a point)
        self._ages = bidict({}) # ages keeps track of how recently something was looked up

    U
    def identify(self, token: str) -> tuple[list[str], int]:
        # if the word is in the cache
        if token in self._cache:
            # update ages to say "token is the most recent one"
            self._ages.inverse[token] = self._current_age
            # current age is incremented by one because we're adding stuff
            self._current_age = self._current_age + 1
            # returns the cached result of identifying token
            return self._cache[token]
        # get the thing to plagerize
        result = self._identifier.identify(token)

        # plagerize
        self._cache[token] = result
        # set the age of token (saying "token is most recent one")
        self._ages[self._current_age] = token
        # increment current age
        self._current_age = self._current_age + 1

        # this is the pruning step to make sure cache isn't too big
        while len(self._cache) > self._buffer_size:
            # if it's set to be killed, kill it
            if self._prune_age in self._ages:
                aged_token = self._ages[self._prune_age]
                # murder
                del self._cache[aged_token]
                del self._ages[self._prune_age]
            # keep pruning until the cache size is below where we want it to be
            self._prune_age = self._prune_age + 1

        return result


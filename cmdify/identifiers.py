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
            while (i == 1 or len(contender[0])) and index + i < len(tokens):
                # adding the next word in tokens
                new_token = new_token + ' ' + tokens[index + i]
                # Literal: sets contender to ([], threshold)
                contender = self.identify(new_token)
                # Literal: contender[1] is always threshold, so the if statement is skipped and the loop ends
                if contender[1] < best[1]:
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
# and a threshold of 0
class LiteralIdentifier(Identifier):
    def identify(self, token: str) -> tuple[list[str], int]:
        # this is used to check for typos 
        # if the word is misstyped, then an empty list is returned
        if token in self.word_index:
            return [self.word_index[token]], 0
        return [], self.threshold


class FuzzyIdentifier(Identifier):

    def identify(self, token: str) -> tuple[list[str], int]:
        if token in self.word_index:
            return [self.word_index[token]], 0
        best = ([], self.threshold)
        for word, keyword in self.word_index.items():
            if abs(len(word) - len(token)) > best[1] + 1:
                continue
            distance = damerau_levenshtein(token, word)
            candidate = [keyword]
            if distance < best[1]:
                best = (candidate, distance)
            elif distance == best[1]:
                candidate.extend(best[0])
                best = (candidate, distance)
        return best


class GraphPruningIdentifier(Identifier):
    def __init__(self, word_index: SynonymReverseIndex, threshold: int):
        super().__init__(word_index, threshold)
        self._graph = {}
        self._populate_graph()

    def _populate_graph(self):
        words = list(self.word_index.keys())
        for word in words:
            self._graph[word] = {x: set() for x in range(1, self.threshold)}
        for i, a in enumerate(words):
            for b in words[i+1:]:
                distance = damerau_levenshtein(a, b)
                if distance < self.threshold:
                    self._graph[a][distance].add(b)
                    self._graph[b][distance].add(a)

    def identify(self, token: str) -> tuple[list[str], int]:
        if token in self.word_index:
            return [self.word_index[token]], 0
        eligible_words = set(self.word_index.keys())
        best = ([], self.threshold)
        for word, keyword in self.word_index.items():
            if abs(len(word) - len(token)) > best[1] + 1 \
                    or word not in eligible_words:
                continue
            distance = damerau_levenshtein(token, word)
            candidate = [keyword]
            if distance < best[1]:
                best = (candidate, distance)
            elif distance == best[1]:
                candidate.extend(best[0])
                best = (candidate, distance)
            else:
                # Prune all words that definitely cannot beat the best, according to the graph
                for i in range(1, self.threshold):
                    if distance - i > best[1]:
                        for irrelevant_word in self._graph[word][i]:
                            eligible_words.discard(irrelevant_word)
                    else:
                        break
        return best


class CachedIdentifier(IdentifierWrapper):
    def __init__(self, identifier: Identifier, buffer_size: int):
        super().__init__(identifier)
        assert buffer_size >= 0
        self._buffer_size = buffer_size
        self._current_age = 0
        self._prune_age = 0
        self._cache = {}
        self._ages = bidict({})

    def identify(self, token: str) -> tuple[list[str], int]:
        if token in self._cache:
            self._ages.inverse[token] = self._current_age
            self._current_age = self._current_age + 1
            return self._cache[token]
        result = self._identifier.identify(token)

        self._cache[token] = result
        self._ages[self._current_age] = token
        self._current_age = self._current_age + 1

        while len(self._cache) > self._buffer_size:
            if self._prune_age in self._ages:
                aged_token = self._ages[self._prune_age]
                del self._cache[aged_token]
                del self._ages[self._prune_age]
            self._prune_age = self._prune_age + 1

        return result


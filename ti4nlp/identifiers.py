import abc
from textdistance import damerau_levenshtein


class Identifier:
    __metaclass__ = abc.ABCMeta

    def __init__(self, word_index, threshold):
        self.word_index = word_index
        self.threshold = threshold

    @abc.abstractmethod
    def find_best(self, token):
        return

    def find_best_from_all(self, tokens):
        tokens = [token.lower() for token in tokens]
        all_results = []
        debt = 0

        for index, token in enumerate(tokens):
            # When we choose to hoard multiple tokens, we use this to skip them
            # when they should be investigated otherwise. Ends up behaving as a
            # greedy algorithm, for better and for worse.
            if debt > 0:
                debt = debt - 1
                continue

            best_token = token
            best = self.find_best(token)
            i = 1
            new_token = token
            contender = ([], 0)  # This is never used but PyCharm seems to care
            while (i == 1 or len(contender[0])) and index + i < len(tokens):
                new_token = new_token + ' ' + tokens[index + i]
                contender = self.find_best(new_token)
                if contender[1] < best[1]:
                    best = contender
                    best_token = new_token
                    debt = i
                i = i + 1

            results = []
            if best[0] is not None:
                [results.append(item) for item in best[0] if item not in results]
            all_results.append((best_token, results))
        return all_results


class LiteralIdentifier(Identifier):
    def find_best(self, token):
        if token in self.word_index.alias_index:
            return [self.word_index.alias_index[token]], 0
        return [], 0


class FuzzyIdentifier(Identifier):

    def find_best(self, token):
        best = ([], self.threshold)
        for word, keyword in self.word_index.alias_index.items():
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
    def __init__(self, word_index, threshold):
        super().__init__(word_index, threshold)
        self.graph = {}
        self._populate_graph()

    def _populate_graph(self):
        words = list(self.word_index.alias_index.keys())
        for word in words:
            self.graph[word] = {x: set() for x in range(1, self.threshold)}
        for i, a in enumerate(words):
            for b in words[i+1:]:
                distance = damerau_levenshtein(a, b)
                if distance < self.threshold:
                    self.graph[a][distance].add(b)
                    self.graph[b][distance].add(a)

    def find_best(self, token):
        eligible_words = set(self.word_index.alias_index.keys())
        best = ([], self.threshold)
        for word, keyword in self.word_index.alias_index.items():
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
                    if distance - i > best[i]:
                        for irrelevant_word in self.graph[word][i]:
                            eligible_words.discard(irrelevant_word)
                    else:
                        break
        return best

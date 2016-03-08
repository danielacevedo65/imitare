from nltk.probability import ConditionalFreqDist, FreqDist, ConditionalProbDist, MLEProbDist
from nltk.util import ngrams

from cfd import SqliteConditionalFreqDist

class NgramModel:

    def __init__(self, words, n, cfd_class=SqliteConditionalFreqDist):
        self._n = n

        if not isinstance(words, list):
            words = list(words)

        cfd = cfd_class()
        for i in range(n):
            for ngram in ngrams(words, i + 1):
                if cfd_class != ConditionalFreqDist:
                    cfd.update_one(ngram[:-1], ngram[-1])
                else:
                    cfd[ngram[:-1]][ngram[-1]] += 1
        if cfd_class != ConditionalFreqDist:
            cfd.commit_replace()
        self._cfd = cfd

    def backoff_search(self, context, backoff_limit, predicate, start_n=None):
        if start_n is not None:
            n = start_n
        else:
            n = self._n
        context = tuple(context)[1 - n:]
        while True:
            while not context in self and len(context) >= backoff_limit:
                context = context[1:]
            choices = FreqDist({word: freq for (word, freq) in self[
                               context].most_common() if predicate(word)})
            if len(choices) > 0:
                return choices
            if len(context) < backoff_limit:
                return None
            context = context[1:]

    def choose_word(self, context, backoff_limit=1, predicate=None):
        return self.generate(1, context, backoff_limit, predicate)[-1]

    def generate(self, num_words, context=[], backoff_limit=1, predicate=None):
        text = list(context)
        for i in range(num_words):
            if predicate is None:
                text.append(self._generate_one(text, backoff_limit))
            else:
                text.append(self._generate_one_predicated(
                    text, backoff_limit, predicate))
        return text

    def _generate_one(self, context, backoff_limit):
        context = tuple(context)[1 - self._n:]
        while not context in self and len(context) >= backoff_limit:
            context = context[1:]
        if context in self:
            return MLEProbDist(self[context]).generate()
        else:
            return None

    def _generate_one_predicated(self, context, backoff_limit, predicate):
        context = tuple(context)[1 - self._n:]
        choices = self.backoff_search(context, backoff_limit, predicate)
        if choices is not None:
            return MLEProbDist(choices).generate()
        else:
            return None

    def __contains__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return item in self._cfd

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return self._cfd[item]

from nltk.probability import ConditionalFreqDist, FreqDist, ConditionalProbDist, MLEProbDist
from nltk.util import ngrams


class NgramModel:

    def __init__(self, words, n):
        self._n = n

        if not isinstance(words, list):
            words = list(words)

        self._cpd = ConditionalProbDist(ConditionalFreqDist((ngram[:-1], ngram[-1]) for ngram in ngrams(words, n)), MLEProbDist)

        if self._n > 2:
            self._backoff = NgramModel(words, n - 1)
        else:
            self._unigram_pd = MLEProbDist(FreqDist(words))

    def backoff_search(self, context, predicate):
        context = tuple(context)[1 - self._n:]
        if context in self:
            choices = FreqDist({word: freq for (word, freq) in self._cpd[context].freqdist().most_common() if predicate(word)})
            if len(choices) > 0:
                return choices
        if self._n > 2:
            return self._backoff.backoff_search(context, predicate)
        else:
            return None

    def choose_word(self, context, predicate=None):
        return self.generate(1, context, predicate)[-1]

    def generate(self, num_words, context=[], predicate=None):
        text = list(context)
        for i in range(num_words):
            if predicate is None:
                text.append(self._generate_one(text))
            else:
                text.append(self._generate_one_predicated(text, predicate))
        return text

    def _generate_one(self, context):
        context = tuple(context)[1 - self._n:]
        if context in self:
            return self._cpd[context].generate()
        elif self._n > 2:
            return self._backoff._generate_one(context)
        else:
            return self._unigram_pd.generate()

    def _generate_one_predicated(self, context, predicate):
        context = tuple(context)[1 - self._n:]
        choices = self.backoff_search(context, predicate)
        if choices is not None:
            return MLEProbDist(choices).generate()
        else:
            # Predicated generate() does not produce a random unigram, as it is
            # slow to filter the entire unigram list repeatedly. Instead, it
            # returns None to indicate that it didn't find a valid word
            return None

    def __contains__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return item in self._cpd

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return self._cpd[item]

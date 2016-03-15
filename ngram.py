"""
Contains the NgramModel class, for generating probable sequences of tokens.
"""

from nltk.probability import ConditionalFreqDist, FreqDist, ConditionalProbDist, MLEProbDist
from nltk.util import ngrams

from cfd import SqliteConditionalFreqDist


class NgramModel:
    """
    Models a sequence of tokens using grams of size <= n
    Supports computing frequency distributions of probable tokens given context and criteria
    """

    def __init__(self, tokens, n, cfd_class=SqliteConditionalFreqDist):
        """
        Parameters
        ----------
        tokens : Iterable
            The token sequence to model
        n : int
            Max size of n-grams to use (warning: larger values take considerably more memory)
        """
        self._n = n

        if not isinstance(tokens, list):
            tokens = list(tokens)
        
        cfd = cfd_class() # Note: currently uses SqliteCFD to save memory

        # Map n-grams to distribution of next-occuring tokens
        for i in range(n):
            # Update conditional frequency distribution
            for ngram in ngrams(tokens, i + 1):
                if cfd_class != ConditionalFreqDist:
                    cfd.update_one(ngram[:-1], ngram[-1])
                else:
                    cfd[ngram[:-1]][ngram[-1]] += 1
        if cfd_class != ConditionalFreqDist:
            cfd.commit_replace()
        self._cfd = cfd


    def backoff_search(self, context, backoff_limit, predicate, start_n=None):
        """
        Finds a frequency distribution of words that match criteria.
        Backs off to successively lower n-grams until non-empty distribution is found. 

        Parameters
        ----------
        context : Iterable
            The current context from which to find possible tokens
        backoff_limit : int
            Stop and return None after reaching backoff_limit sized n-grams during backoff
        predicate : Token -> bool
            If predicate(token) is False, token is ignored and excluded from result.
            Search continues until result is non-empty, or another stopping condition is reached.
        start_n : int
            Start with n-grams of a lower size than of the model

        Returns
        -------
        FreqDist
            Frequency distribution of token occurences given the context and predicate.
        None
            If search did not find any possible tokens.
        """
        if start_n is not None:
            n = start_n
        else:
            n = self._n
        context = tuple(context)[1 - n:] # Start at n-gram specified
        while True:
            while not context in self and len(context) >= backoff_limit:
                context = context[1:]
            choices = FreqDist({word: freq for (word, freq) in self[
                               context].most_common() if predicate(word)})
            if len(choices) > 0: # Search was successful
                return choices
            if len(context) < backoff_limit:
                return None
            context = context[1:] # Backoff to (n-1)-gram


    def generate(self, num_toks, context=[], backoff_limit=1, predicate=None):
        """
        Generates successive tokens given the context and criteria
        Uses maximum-likelihood probability to randomly select from possible token frequency distributions

        Parameters
        ----------
        num_toks : int
            How many tokens to generate
        *
            Rest of parameters are passed to backoff_search

        Returns
        -------
        Iterable:
            Sequence of tokens starting with context and appended with num_toks of generated tokens
        """

        text = list(context)
        for i in range(num_toks):
            if predicate is None: # Use faster version if no predicate
                text.append(self._generate_one(text, backoff_limit))
            else:
                text.append(self._generate_one_predicated(
                    text, backoff_limit, predicate))
        return text

    def choose_word(self, context, backoff_limit=1, predicate=None):
        """
        Generates a single token with generate
        """
        return self.generate(1, context, backoff_limit, predicate)[-1]

    def _generate_one(self, context, backoff_limit):
        context = tuple(context)[1 - self._n:]
        while not context in self and len(context) >= backoff_limit:
            context = context[1:]
        if context in self:
            return MLEProbDist(self[context]).generate() # Select from possible tokens
        else:
            return None

    def _generate_one_predicated(self, context, backoff_limit, predicate):
        context = tuple(context)[1 - self._n:]
        choices = self.backoff_search(context, backoff_limit, predicate) # Possible tokens
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

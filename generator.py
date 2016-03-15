"""
Implements the main algorithm for generating text
"""

from nltk.probability import FreqDist, ConditionalFreqDist, MLEProbDist
from ngram import NgramModel
import random


class WordIdDictionary:
    """
    Mapping for word to id transformations
    Conversion saves memory and speeds up the pipeline
    """

    def __init__(self, words=[]):
        """
        Parameters
        ----------
        words : Iterable[str]
            Gather unique from words to assign ids to
        """
        self._count = 0
        self._to_id = dict()
        self._to_word = dict()

        self.add_words(words)

    def add_words_transform(self, words):
        self.add_words(words)
        return self.transform_words(words)

    def add_words(self, words):
        for word in words:
            self._possibly_add_word(word)

    def _possibly_add_word(self, word):
        if not word in self._to_id:
            self._to_id[word] = self._count
            self._to_word[self._count] = word
            self._count += 1

    def transform_word(self, word):
        return self._to_id[word]

    def transform_id(self, id):
        return self._to_word[id]

    def transform_words(self, words):
        return map(lambda word: self._to_id[word], words)

    def transform_ids(self, ids):
        return map(lambda id: self._to_word[id], ids)


class LVGNgramGenerator:
    """
    Lemmatized vocabulary and grammar ngram-based generator
    """

    def __init__(self, tuples, n):
        """
        Parameters
        ----------
        tuples : Iterable[(str, str, str)]
            A list of (word, lemma, tag) tuples from which to learn a model
        n : int
            Maximum size of n-grams to use in NgramModel
        """
        self._n = n
        print("Creating models... (this may take some time)");
        self._make_models(tuples)
        print("Done!");

    def _make_models(self, tuples):
        self._word_ids = WordIdDictionary()

        # Extract sequence of words, lemmas, and tags
        words, lemmas, tags = tuple(map(lambda tokens: list(
            self._word_ids.add_words_transform(tokens)), zip(*tuples)))
        self._tags = tags

        # Create models for words, lemmas, and tags
        self._words_ngram = NgramModel(words, self._n)
        self._lemmas_ngram = NgramModel(lemmas, self._n)
        self._tags_ngram = NgramModel(tags, 2 * self._n) # Can afford to use 2 * n-gram size for grammar

        # Map tag and (tag, lemma) to valid lemmas and vocabulary, respectively
        # It's faster to use a list than predicate on unigrams during backoff search
        self._tag_lemmas = ConditionalFreqDist(zip(tags, lemmas))
        self._tag_lemma_words = ConditionalFreqDist(
            zip(zip(tags, lemmas), words))

    def generate_without_pos(self, n):
        """
        Generate n words without using any special POS information
        """
        # Just use words NgramModel generate function
        generated_words = self._words_ngram.generate(n)
        return list(self._word_ids.transform_ids(generated_words))

    def generate(self, n):
        """
        Generate n words using copied grammar, generated lemmas, and words based on lemmas
        """
        start = random.randint(n, len(self._tags) - n)
        generated_tags = self._tags[start : start + n] # Copy a random section of POS tags for grammar

        # Generate sequence of lemmas based off of grammar
        generated_lemmas = []
        for tag in generated_tags:
            # Search for and choose a lemma with correct tag
            choice = self._lemmas_ngram.choose_word(
                generated_lemmas, backoff_limit=2, predicate=lambda lemma: lemma in self._tag_lemmas[tag])
            if choice is None: 
                # Could not find a good lemma for current POS tag, choose from list
                choice = MLEProbDist(self._tag_lemmas[tag]).generate()
            generated_lemmas.append(choice)

        # Generate sequence of words based off of lemmas and grammar
        generated_words = []
        for (tag, lemma) in zip(generated_tags, generated_lemmas):
            # Search for and choose word with correct lemma/tag
            choices = self._words_ngram.backoff_search(
                generated_words, backoff_limit=2, predicate=lambda word: word in self._tag_lemma_words[(tag, lemma)])
            if choices is None:
                # Could not find a good word, choose from list
                choices = self._tag_lemma_words[(tag, lemma)]
            generated_words.append(MLEProbDist(choices).generate())

        return list(self._word_ids.transform_ids(generated_words))

    def generate_alternative(self, n):
        """
        Generate n words using a more complicated algorithm
        """
        generated_tags = []
        generated_lemmas = []
        generated_words = []

        # Incrementally generate (tag, lemma) pairs
        for i in range(n):
            tag_choice = None # Start with nothing

            # Loop through n-grams of grammar
            size = 2 * self._n
            while size > 2:
                tag_choices = self._tags_ngram.backoff_search(
                    generated_tags, backoff_limit=2, predicate=lambda tag: True, start_n=size)

                # Determine valid lemmas in context with these tag choices
                tag_to_lemma = {}
                if tag_choices is not None:
                    for tag, _ in tag_choices.items():
                        # For each tag, find valid lemmas in context with that tag
                        lemma = self._lemmas_ngram.choose_word(
                            generated_lemmas, backoff_limit=2, predicate=lambda lemma: lemma in self._tag_lemmas[tag])
                        if lemma is not None:
                            tag_to_lemma[tag] = lemma

                    if len(tag_to_lemma) > 1:
                        # We have found valid (tag, lemma) pairs
                        tag_probdist = MLEProbDist(FreqDist(
                            {tag: freq for tag, freq in tag_choices.items() if tag in tag_to_lemma}))
                        tag_choice = tag_probdist.generate() # Randomly select the tag
                        lemma_choice = tag_to_lemma[tag_choice] # Set the lemma
                        break
                size -= 1 # Lower to smaller n-gram for more tag choices

            if tag_choice is None:
                # We still didn't find a valid (tag, lemma) pair, fallback
                tag_choice = MLEProbDist(tag_choices).generate()
                lemma_choice = MLEProbDist(
                    self._tag_lemmas[tag_choice]).generate()

            generated_tags.append(tag_choice)
            generated_lemmas.append(lemma_choice)

        # Generate all words based on (tag, lemma) pairs
        for (tag, lemma) in zip(generated_tags, generated_lemmas):
            # Search for and choose word with correct lemma/tag
            choices = self._words_ngram.backoff_search(
                generated_words, backoff_limit=2, predicate=lambda word: word in self._tag_lemma_words[(tag, lemma)])
            if choices is None:
                # Could not find a good word, choose from list
                choices = self._tag_lemma_words[(tag, lemma)]
            generated_words.append(MLEProbDist(choices).generate())

        return list(self._word_ids.transform_ids(generated_words))

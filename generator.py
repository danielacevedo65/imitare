from nltk.probability import FreqDist, ConditionalFreqDist, MLEProbDist
from ngram import NgramModel
import random


class WordIdDictionary:
    """ Mapping for word <-> id transformation """

    def __init__(self, words=[]):
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
    """ Lemmatized vocubulary and grammar ngram-based generator """

    def __init__(self, tuples, n):
        self._n = n
        self._make_models(tuples)

    def _make_models(self, tuples):
        self._word_ids = WordIdDictionary()

        words, lemmas, tags = tuple(map(lambda tokens: list(
            self._word_ids.add_words_transform(tokens)), zip(*tuples)))
        self._tags = tags
        self._words_ngram = NgramModel(words, self._n)
        self._lemmas_ngram = NgramModel(lemmas, self._n)
        self._tags_ngram = NgramModel(tags, 2 * self._n)

        self._tag_lemmas = ConditionalFreqDist(zip(tags, lemmas))
        self._tag_lemma_words = ConditionalFreqDist(
            zip(zip(tags, lemmas), words))

    def generate_without_pos(self, n):
        generated_words = self._words_ngram.generate(n)
        return list(self._word_ids.transform_ids(generated_words))

    def generate(self, n):
        start = random.randint(n, len(self._tags) - n)
        generated_tags = self._tags[start : start + n]
        #generated_tags = self._tags_ngram.generate(n)

        generated_lemmas = []
        for tag in generated_tags:
            choice = self._lemmas_ngram.choose_word(
                generated_lemmas, backoff_limit=2, predicate=lambda lemma: lemma in self._tag_lemmas[tag])
            if choice is None:
                choice = MLEProbDist(self._tag_lemmas[tag]).generate()
                print("forced to generate lemma",
                      self._word_ids.transform_id(choice))
            generated_lemmas.append(choice)

        generated_words = []
        for (tag, lemma) in zip(generated_tags, generated_lemmas):
            choices = self._words_ngram.backoff_search(
                generated_words, backoff_limit=2, predicate=lambda word: word in self._tag_lemma_words[(tag, lemma)])
            if choices is None:
                choices = self._tag_lemma_words[(tag, lemma)]
                print("forced to generate words", repr({self._word_ids.transform_id(
                    choice): freq for choice, freq in choices.items()}))
            generated_words.append(MLEProbDist(choices).generate())

        return list(self._word_ids.transform_ids(generated_words))

    def generate_alternative(self, n):
        generated_tags = []
        generated_lemmas = []
        generated_words = []

        for i in range(n):
            tag_choice = None

            size = 2 * self._n
            while size > 2:
                tag_choices = self._tags_ngram.backoff_search(
                    generated_tags, backoff_limit=2, predicate=lambda tag: True, start_n=size)
                tag_to_lemma = {}
                if tag_choices is not None:
                    for tag, _ in tag_choices.items():
                        lemma = self._lemmas_ngram.choose_word(
                            generated_lemmas, backoff_limit=2, predicate=lambda lemma: lemma in self._tag_lemmas[tag])
                        if lemma is not None:
                            tag_to_lemma[tag] = lemma
                    if len(tag_to_lemma) > 1:
                        tag_probdist = MLEProbDist(FreqDist(
                            {tag: freq for tag, freq in tag_choices.items() if tag in tag_to_lemma}))
                        tag_choice = tag_probdist.generate()
                        lemma_choice = tag_to_lemma[tag_choice]
                        break
                size -= 1

            if tag_choice is None:
                tag_choice = MLEProbDist(tag_choices).generate()
                lemma_choice = MLEProbDist(
                    self._tag_lemmas[tag_choice]).generate()
                print("forced to generate lemma",
                      self._word_ids.transform_id(lemma_choice))

            generated_tags.append(tag_choice)
            generated_lemmas.append(lemma_choice)

        for (tag, lemma) in zip(generated_tags, generated_lemmas):
            choices = self._words_ngram.backoff_search(
                generated_words, backoff_limit=2, predicate=lambda word: word in self._tag_lemma_words[(tag, lemma)])
            if choices is None:
                choices = self._tag_lemma_words[(tag, lemma)]
                print("forced to generate words", repr({self._word_ids.transform_id(
                    choice): freq for choice, freq in choices.items()}))
            generated_words.append(MLEProbDist(choices).generate())

        return list(self._word_ids.transform_ids(generated_words))

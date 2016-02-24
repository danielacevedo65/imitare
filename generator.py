from nltk.probability import ConditionalFreqDist, MLEProbDist
from ngram import NgramModel


class LVGNgramGenerator:
    """ Lemmatized vocubulary and grammar ngram-based generator """

    def __init__(self, tagged, n):
        self._n = n
        if not isinstance(tagged, list):
            tagged = list(tagged)
        self._tagged = tagged
        self._learn_models()

    def _learn_models(self):
        self._lemmas_ngram = NgramModel(self._yield_lemmas(), self._n)
        self._tags_ngram = NgramModel(self._yield_tags(), self._n)

        self._tag_lemmas = ConditionalFreqDist(
            (tag, lemma) for (_, lemma, tag) in self._tagged)
        self._tag_lemma_words = ConditionalFreqDist(
            ((tag, lemma), word) for (word, lemma, tag) in self._tagged)

    def generate(self, n):
        generated_tags = self._tags_ngram.generate(n)

        generated_lemmas = []
        for tag in generated_tags:
            choice = self._lemmas_ngram.choose_word(
                generated_lemmas, lambda lemma: lemma in self._tag_lemmas[tag])
            if choice is None:
                choice = MLEProbDist(self._tag_lemmas[tag]).generate()
            generated_lemmas.append(choice)

        generated_words = []
        for (tag, lemma) in zip(generated_tags, generated_lemmas):
            generated_words.append(MLEProbDist(
                self._tag_lemma_words[(tag, lemma)]).generate())

        return generated_words

    def _yield_tags(self):
        for (_, _, tag) in self._tagged:
            yield tag

    def _yield_lemmas(self):
        for (_, lemma, _) in self._tagged:
            yield lemma

    def _yield_words(self):
        for (word, _, _) in self._tagged:
            yield word

if __name__ == '__main__':
    import sys
    from stanford import StanfordTagger

    if len(sys.argv) != 3:
        print("usage: python", sys.argv[0], "input_file n")
        print("    input_file: learn a model from this text file")
        print("    n: n for the ngram model")
        sys.exit(1)

    with open(sys.argv[1]) as input_file:
        text = input_file.read()

    tagged = StanfordTagger().tag(text)
    model = LVGNgramGenerator(tagged, int(sys.argv[2]))

    while True:
        num_words = input(
            'Enter the length in words to generate (or "quit" to exit): ')
        if num_words.isdigit():
            print(' '.join(model.generate(int(num_words))))
        elif num_words == 'quit':
            break

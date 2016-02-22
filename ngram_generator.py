import nltk
from NgramModel import NgramModel
from collections import defaultdict

class ngram_generator:

    def __init__(self, tagged_words, n):
        self._tagged_words = tagged_words
        self._n = n
        self._learn_models()

    def _learn_models(self):
        self._vocab_ngram = NgramModel(self._n, list(self._yield_words())) 
        self._grammar_ngram = NgramModel(self._n, list(self._yield_tags()))

        self._tag_to_freqdist = defaultdict(nltk.FreqDist)
        for (word, tag) in self._tagged_words:
            self._tag_to_freqdist[tag].update([word])

        self._tagged_word_kinds = frozenset(self._tagged_words)

    def _choose_word_by_tag(self, tag, model, context=()):
        if len(context) == 0:
            return nltk.ELEProbDist(self._tag_to_freqdist[tag]).generate()
        else:
            context = (model._lpad + tuple(context))[1 - model._n:]
            if context in model:
                freqdist = nltk.FreqDist()
                for (word, freq) in model[context].freqdist().most_common():
                    if (word, tag) in self._tagged_word_kinds:
                        freqdist += nltk.FreqDist({word: freq})
                
                print("context with freqdist", repr(freqdist))
                if len(freqdist) > 0:
                    return nltk.ELEProbDist(freqdist).generate()
            if model._n > 1:
                print("backing off:", context)
                return self._choose_word_by_tag(tag, model.backoff, context)
            else:
                print("no alternative")
                return nltk.ELEProbDist(self._tag_to_freqdist[tag]).generate()

    def generate(self, n):
        generated_tags = self._grammar_ngram.generate(100 + n)[-n:]
        
        generated_words = []
        for tag in generated_tags:
            generated_words.append(self._choose_word_by_tag(tag, self._vocab_ngram, generated_words))

        return generated_words 

    def _yield_tags(self):
        for (_, tag) in self._tagged_words:
            yield tag

    def _yield_words(self):
        for (word, _) in self._tagged_words:
            yield word

if __name__ == '__main__':
    import sys
    from tokenizer import stanford_tokenizer
    from postagger import stanford_postagger

    if len(sys.argv) != 3:
        print("usage: python", sys.argv[0], "input_file n")
        print("    input_file: learn a model from this text file")
        print("    n: n for the ngram model")
        sys.exit(1)

    with open(sys.argv[1]) as input_file:
        text = input_file.read()

    # large text might cause an out of memory exception, let's make sure that doesn't happen
    split_by_space = text.split(' ')

    tagged = []
    for i in range(0, len(split_by_space), 20000): # tagging 20000 words takes about 2gB of ram
        tagged += stanford_postagger().tag(stanford_tokenizer().tokenize(' '.join(split_by_space[i:i+20000]))) 

    model = ngram_generator(tagged, int(sys.argv[2]))

    while True:
        num_words = input("Enter the length in words to generate: ")
        if num_words.isdigit():
            print(' '.join(model.generate(int(num_words))))

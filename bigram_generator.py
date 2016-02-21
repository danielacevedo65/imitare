import nltk
from collections import defaultdict

class bigram_generator:

    def __init__(self, tagged_words):
        self._tagged_words = tagged_words
        self._learn_models()

    def _learn_models(self):
        self._vocab_cfd = nltk.ConditionalFreqDist(nltk.bigrams(self._yield_words())) 
        self._grammar_cfd = nltk.ConditionalFreqDist(nltk.bigrams(self._yield_tags()))

        self._tag_to_freqdist = defaultdict(nltk.FreqDist)
        for (word, tag) in self._tagged_words:
            self._tag_to_freqdist[tag].update([word])

        self._tagged_word_kinds = frozenset(self._tagged_words)

    def generate(self, n):
        generated_tags = []

        tag = '.'
        for _ in range(n):
            generated_tags.append(tag)
            if len(self._grammar_cfd[tag]) == 0:
                break
            tag = nltk.ELEProbDist(self._grammar_cfd[tag]).generate()

        generated_words = []
        
        word = '.'
        for i in range(n):
            generated_words.append(word)

            freqdist = nltk.FreqDist() 
            for (word, freq) in self._vocab_cfd[word].most_common():
                if (word, generated_tags[i]) in self._tagged_word_kinds:
                    freqdist += nltk.FreqDist({word: freq})

            if len(freqdist) == 0:
                freqdist = self._tag_to_freqdist[generated_tags[i]]

            word = nltk.ELEProbDist(freqdist).generate() 

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

    if len(sys.argv) != 2:
        print("usage: python", sys.argv[0], "input_file")
        print("    input_file: learn a model from this text file")
        sys.exit(1)

    with open(sys.argv[1]) as input_file:
        text = input_file.read()

    model = bigram_generator(stanford_postagger().tag(stanford_tokenizer().tokenize(text)))

    while True:
        num_words = input("Enter the length in words to generate: ")
        if num_words.isdigit():
            print(model.generate(int(num_words)))

from stanford import StanfordTagger, StanfordDetokenizer
from generator import LVGNgramGenerator
import random
import csv

def twitter(file: str, n: int, words: int, method: str):
    '''raw_file -> name of file
       n -> number of n-grams
       words -> how many to generate
       method -> method used to generate
    '''
    file = open(file, 'r')
    text = file.read()
    tagged = StanfordTagger(verbose=True).tag(text)
    file.close()

    detok = StanfordDetokenizer()
    model = LVGNgramGenerator(tagged, n)
    methods = {'b': model.generate_without_pos, 'n': model.generate, 't': model.generate_alternative}
    result = []
    x = 0
    while x < words:
        num_words = str(random.randint(20, 65))
        if num_words.isdigit():
            if method in methods:
                result.append(detok.detokenize(' '.join(methods[method](int(num_words)))))
        x += 1
    final = []
    for i in result:
        if i.startswith("forced"):
            pass
        else:
            final.append(i)
    return final
    
def yelp_or_gutenberg(file: str, n: int, words: int, method: str):        
    file = open(file, 'r')
    tag = csv.reader(file)
    tagged = []
    try:
        for row in tag:
            tagged.append(tuple(row))
    except:
        pass
    file.close()
    detok = StanfordDetokenizer()
    model = LVGNgramGenerator(tagged, n)
    methods = {'b': model.generate_without_pos, 'n': model.generate, 't': model.generate_alternative}
    x = 0
    result = []
    final = []    
    while x < words:
        num_words = str(random.randint(20, 65))
        if num_words.isdigit():
            if method in methods:
                result.append(detok.detokenize(' '.join(methods[method](int(num_words)))))
        x += 1
    for i in result:
        if i.startswith("forced"):
            pass
        else:
            final.append(i)
    return final
        

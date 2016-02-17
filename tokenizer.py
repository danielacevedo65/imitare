from nltk.tokenize import StanfordTokenizer
from nltk.internals import find_jars_within_path

_stanford_tokenizer = StanfordTokenizer(path_to_jar='stanford-postagger/stanford-postagger.jar')
_stanford_tokenizer._stanford_jar = ':'.join(find_jars_within_path('stanford-postagger'))

def stanford_tokenizer():
    return _stanford_tokenizer

if __name__ == '__main__':
    import sys
    tokenizer = stanford_tokenizer()
    
    try:
        for line in sys.stdin:
            print(tokenizer.tokenize(line))
    except KeyboardInterrupt:
        pass

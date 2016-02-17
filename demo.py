from tokenizer import stanford_tokenizer
from postagger import stanford_postagger

def stanford_pipeline(text):
    tokenizer = stanford_tokenizer()
    postagger = stanford_postagger()

    return postagger.tag(tokenizer.tokenize(text))

if __name__ == '__main__':
    import sys

    try:
        for line in sys.stdin:
            print(stanford_pipeline(line))
    except KeyboardInterrupt:
        pass

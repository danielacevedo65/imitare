import argparse
import csv
from stanford import StanfordTagger, StanfordDetokenizer
from generator import LVGNgramGenerator

def main(raw_file, tagged_file, save_file, n):
    if raw_file is not None:
        text = raw_file.read()
        tagged = StanfordTagger(verbose=True).tag(text)
        raw_file.close()
        if save_file is not None:
            save = csv.writer(save_file)
            save.writerows(tagged)
            save_file.close()
    elif tagged_file is not None:
        tagged = csv.reader(tagged_file)
        tagged = [tuple(row) for row in tagged]
        tagged_file.close()

    detok = StanfordDetokenizer()
    model = LVGNgramGenerator(tagged, n)
    methods = {'b': model.generate_without_pos, 'n': model.generate, 't': model.generate_alternative}
    while True:
        num_words = input('Enter the length in words to generate (or "q" to exit): ')
        if num_words.isdigit():
            method = input('Enter a generation method {b: baseline, n: normal, t: tuned}: ')
            if method in methods:
                print(detok.detokenize(' '.join(methods[method](int(num_words)))))
        elif num_words == 'q':
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demo the projects current text generator')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--raw', type=argparse.FileType('r'), help='use untagged text file for model creation')
    group.add_argument('--tagged', type=argparse.FileType('r'), help='use tagged file for model creation')
    parser.add_argument('--save', type=argparse.FileType('w'), help='save tagged file for later use')
    parser.add_argument('n', type=int, help='maximum length of ngrams to use')

    args = parser.parse_args()
    main(raw_file=args.raw, tagged_file=args.tagged, save_file=args.save, n=args.n)

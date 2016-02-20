from nltk.tag import StanfordPOSTagger
from nltk.internals import find_jars_within_path

_stanford_postagger = StanfordPOSTagger('stanford-postagger/models/english-bidirectional-distsim.tagger', path_to_jar='stanford-postagger/stanford-postagger.jar', java_options='-mx2g')
_stanford_postagger._stanford_jar = ':'.join(find_jars_within_path('stanford-postagger'))

def stanford_postagger():
    return _stanford_postagger

if __name__ == '__main__':
    import sys
    tagger = stanford_postagger()
    
    try:
        for line in sys.stdin:
            print(tagger.tag(line.split()))
    except KeyboardInterrupt:
        pass

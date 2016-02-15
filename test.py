from nltk.tag import StanfordPOSTagger

def bug_workaround_stanford_slf4j_jars():
    from nltk.internals import find_jars_within_path
    stanford_dir = 'stanford-postagger'
    stanford_jars = find_jars_within_path(stanford_dir)
    st._stanford_jar = ':'.join(stanford_jars)

st = StanfordPOSTagger('stanford-postagger/models/english-bidirectional-distsim.tagger', path_to_jar='stanford-postagger/stanford-postagger.jar')
bug_workaround_stanford_slf4j_jars()

print(st.tag('What is the airspeed of an unladen swallow ?'.split()))

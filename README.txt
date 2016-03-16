Notes
-----
NLTK and other libraries listed under each file are required to run them.
More documentation can be found within each file.

Important Files
---------------
imitare.py
    Console interface for generating text.
    Requires: matplotlib, twython

generator.py
    Algorithms for text generation. Creates NgramModels for tags, lemmas, and vocabulary.
    Implements baseline, normal, and tuned algorithms.

ngram.py
    NgramModel class. Provides likely next words given a context and other criteria.
    Implements backoff to search smaller n-gram sizes.

stanford.py
    Python interfaces to Stanford NLP libraries.

cfd.py
    Better memory-conserving ConditionalFrequencyDistribution classes.
    Requires: sqlite3 program

generate_yelp_data.py
    Generate text file of a subset of reviews from the Yelp dataset.

Twitter_data.py
    Generate text file of Tweets from a Twitter user.
    Requires: twython

webpage_demo.py
    Web interface for generating text. Starts a web server.
    Requires: matplotlib, twython, flask

stanford/*
    Stanford NLP libraries and models.

data/*
    Preprocessed and tagged data for use with generator algorithms.

from nltk.probability import ConditionalFreqDist, FreqDist, ConditionalProbDist, MLEProbDist
from nltk.util import ngrams

import sqlite3
import pickle

def _sqlite_register_pickle(typecls, typename):
    sqlite3.register_adapter(typecls, pickle.dumps)
    sqlite3.register_converter(typename, pickle.loads)

_sqlite_register_pickle(tuple, 'tuple')
_sqlite_register_pickle(dict, 'dict')

class SqliteConditionalFreqDist:
    def __init__(self, cond_samples=[], database=':memory:'):
        self._journal = ConditionalFreqDist()
        self._journal_count = 0
        
        conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        self._sql = conn.cursor()
        self._sql.execute('create table cfd(k tuple unique primary key, v dict)')

        self.update(cond_samples)

    def update(self, cond_samples):
        for (cond, sample) in cond_samples:
            self._journal[cond][sample] += 1

    def update_one(self, cond, sample):
        self._journal[cond][sample] += 1

    def commit(self):
        cfd = self._journal
        self._journal = ConditionalFreqDist()

        for cond in cfd.keys():
            olddist = self[cond]
            cfd[cond] += olddist

        self._sql.executemany('insert or replace into cfd(k, v) values (?, ?)', ((cond, dict(freqdist)) for cond,freqdist in cfd.items()))
        
    def commit_replace(self):
        cfd = self._journal
        self._journal = ConditionalFreqDist()

        self._sql.executemany('insert or replace into cfd(k, v) values (?, ?)', ((cond, dict(freqdist)) for cond,freqdist in cfd.items()))

    def __getitem__(self, key):
        self._sql.execute('select v from cfd where k = (?)', (key,))
        value = self._sql.fetchall()
        if len(value) > 0:
            return FreqDist(value[0][0])
        else:
            return FreqDist() 

    def __setitem__(self, key, value):
        value = dict(value)
        self._sql.execute('insert or replace into cfd(k, v) values (?, ?)', (key, value))

    def __contains__(self, key):
        self._sql.execute('select v from cfd where k = (?)', (key,))
        value = self._sql.fetchall()
        return len(value) > 0

class NgramModel:

    def __init__(self, words, n, cfd_class=SqliteConditionalFreqDist):
        self._n = n

        if not isinstance(words, list):
            words = list(words)

        cfd = cfd_class()
        for i in range(n):
            for ngram in ngrams(words, i + 1):
                if cfd_class == SqliteConditionalFreqDist:
                    cfd.update([(ngram[:-1], ngram[-1])])
                else:
                    cfd[ngram[:-1]][ngram[-1]] += 1
        if cfd_class == SqliteConditionalFreqDist:
            cfd.commit_replace()
        self._cfd = cfd

    def backoff_search(self, context, backoff_limit, predicate):
        context = tuple(context)[1 - self._n:]
        while True:
            while not context in self and len(context) >= backoff_limit:
                context = context[1:]
            choices = FreqDist({word: freq for (word, freq) in self[
                               context].most_common() if predicate(word)})
            if len(choices) > 0:
                return choices
            if len(context) < backoff_limit:
                return None
            context = context[1:]

    def choose_word(self, context, backoff_limit=1, predicate=None):
        return self.generate(1, context, backoff_limit, predicate)[-1]

    def generate(self, num_words, context=[], backoff_limit=1, predicate=None):
        text = list(context)
        for i in range(num_words):
            if predicate is None:
                text.append(self._generate_one(text, backoff_limit))
            else:
                text.append(self._generate_one_predicated(
                    text, backoff_limit, predicate))
        return text

    def _generate_one(self, context, backoff_limit):
        context = tuple(context)[1 - self._n:]
        while not context in self and len(context) >= backoff_limit:
            context = context[1:]
        if context in self:
            return MLEProbDist(self[context]).generate()
        else:
            return None

    def _generate_one_predicated(self, context, backoff_limit, predicate):
        context = tuple(context)[1 - self._n:]
        choices = self.backoff_search(context, backoff_limit, predicate)
        if choices is not None:
            return MLEProbDist(choices).generate()
        else:
            return None

    def __contains__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return item in self._cfd

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        return self._cfd[item]

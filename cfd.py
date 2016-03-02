from nltk.probability import ConditionalFreqDist, FreqDist

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

        conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        self._sql = conn.cursor()
        self._sql.execute(
            'create table cfd(k tuple, v dict)')

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

        self._sql.executemany('insert or replace into cfd(k, v) values (?, ?)', ((
            cond, dict(freqdist)) for cond, freqdist in cfd.items()))

    def commit_replace(self):
        cfd = self._journal
        self._journal = ConditionalFreqDist()

        self._sql.executemany('insert or replace into cfd(k, v) values (?, ?)', ((
            cond, dict(freqdist)) for cond, freqdist in cfd.items()))

        self._commit_finalize()

    def _commit_finalize(self):
        self._sql.execute(
            'create unique index kidx on cfd(k)')

    def __getitem__(self, key):
        self._sql.execute('select v from cfd where k = (?)', (key,))
        value = self._sql.fetchall()
        if len(value) > 0:
            return FreqDist(value[0][0])
        else:
            return FreqDist()

    def __setitem__(self, key, value):
        value = dict(value)
        self._sql.execute(
            'insert or replace into cfd(k, v) values (?, ?)', (key, value))

    def __contains__(self, key):
        self._sql.execute('select v from cfd where k = (?)', (key,))
        value = self._sql.fetchall()
        return len(value) > 0


class PickleConditionalFreqDist:

    def __init__(self, cond_samples=[]):
        self._journal = ConditionalFreqDist()

        self._store = dict()
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
            self[cond] = cfd[cond]

    def commit_replace(self):
        cfd = self._journal
        self._journal = ConditionalFreqDist()

        for cond in cfd.keys():
            newdist = self[cond]
            newdist += cfd[cond]
            self[cond] = newdist

    def __getitem__(self, key):
        key = pickle.dumps(key)
        if key in self._store:
            return FreqDist(pickle.loads(self._store[key]))
        else:
            return FreqDist()

    def __setitem__(self, key, value):
        key = pickle.dumps(key)
        value = dict(value)
        self._store[key] = pickle.dumps(value)

    def __contains__(self, key):
        key = pickle.dumps(key)
        return key in self._store

"""
Implements various attempts to conserve memory using a better ConditionalFreqDist class.
Python dicts unfortunately have huge byte cost even when nearly empty.
"""

from nltk.probability import ConditionalFreqDist, FreqDist

import sqlite3
import pickle

# Functions for memory usage aware persisting to Sqlite3 database
def _write_var_uint(uint):
    bytes = bytearray()
    while uint > 127:
        bytes.append((uint & 127) | 128)
        uint >>= 7
    bytes.append(uint & 127)
    return bytes


def _write_var_uint_to(uint, bytes):
    while uint > 127:
        bytes.append((uint & 127) | 128)
        uint >>= 7
    bytes.append(uint & 127)


def _read_var_uint(bytes):
    uint = 0
    for (i, byte) in enumerate(bytes):
        uint += (byte & 127) << (7 * i)
        if byte & 128 == 0:
            break
    return (uint, i + 1)


def _compact_write_ints(iterable):
    bytes = bytearray()
    for i in iterable:
        _write_var_uint_to(i, bytes)
    return bytes


def _compact_read_ints(bytes):
    output = []
    while len(bytes) > 0:
        uint, read = _read_var_uint(bytes)
        bytes = bytes[read:]
        output.append(uint)
    return output


def _compact_inttuple_write(t):
    return _compact_write_ints(t)


def _compact_inttuple_read(bytes):
    return tuple(_compact_read_ints(bytes))


def _compact_FreqDist_write(d):
    def yield_kvs(d):
        for k, v in d.items():
            yield k
            yield v
    return _compact_write_ints(yield_kvs(d))


def _compact_intdict_read(bytes):
    ints = _compact_read_ints(bytes)
    return {k: v for (k, v) in zip(ints[::2], ints[1::2])}

sqlite3.register_adapter(tuple, _compact_inttuple_write)
sqlite3.register_converter("tuple", _compact_inttuple_read)
sqlite3.register_adapter(FreqDist, _compact_FreqDist_write)
sqlite3.register_converter("FreqDist", _compact_intdict_read)

#def _sqlite_register_pickle(typecls, typename):
#    sqlite3.register_adapter(typecls, pickle.dumps)
#    sqlite3.register_converter(typename, pickle.loads)
#
#_sqlite_register_pickle(tuple, 'tuple')
#_sqlite_register_pickle(dict, 'dict')


class SqliteConditionalFreqDist:
    """
    Mimicks a ConditionalFreqDist from ntlk using a Sqlite3 backend.
    Note: assumes only int types, specifically tuple(int) mapping to FreqDist(int)
    """

    def __init__(self, cond_samples=[], database=':memory:'):
        self._journal = ConditionalFreqDist()

        conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        self._sql = conn.cursor()
        self._sql.execute(
            'create table cfd(k tuple unique primary key, v FreqDist)')

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
            cond, freqdist) for cond, freqdist in cfd.items()))

    def commit_replace(self):
        cfd = self._journal
        self._journal = ConditionalFreqDist()

        self._sql.executemany('insert or replace into cfd(k, v) values (?, ?)', ((
            cond, freqdist) for cond, freqdist in cfd.items()))

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
    """
    Mimicks a ConditionalFreqDist from ntlk using Picklefied dicts to save memory.
    """

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

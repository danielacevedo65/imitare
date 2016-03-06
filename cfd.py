from nltk.probability import ConditionalFreqDist, FreqDist

import sqlite3
import pickle


def _write_var_uint(uint):
    output = bytearray()
    while uint > 127:
        output.append((uint & 127) | 128)
        uint >>= 7
    output.append(uint & 127)
    return output


def _read_var_uint(bytes):
    uint = 0
    for (i, byte) in enumerate(bytes):
        uint += (byte & 127) << (7 * i)
        if byte & 128 == 0:
            break
    return (uint, i + 1)


def _compact_write_ints(iterable):
    output = bytearray()
    for i in iterable:
        output += _write_var_uint(i)
    return output


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


def _compact_intdict_write(d):
    ints = []
    for k, v in d.items():
        ints.extend((k, v))
    return _compact_write_ints(ints)


def _compact_intdict_read(bytes):
    ints = _compact_read_ints(bytes)
    return {k: v for (k, v) in zip(ints[::2], ints[1::2])}

sqlite3.register_adapter(tuple, _compact_inttuple_write)
sqlite3.register_converter("tuple", _compact_inttuple_read)
sqlite3.register_adapter(dict, _compact_intdict_write)
sqlite3.register_converter("dict", _compact_intdict_read)

##def _sqlite_register_pickle(typecls, typename):
##    sqlite3.register_adapter(typecls, pickle.dumps)
##    sqlite3.register_converter(typename, pickle.loads)
##
##_sqlite_register_pickle(tuple, 'tuple')
##_sqlite_register_pickle(dict, 'dict')


class SqliteConditionalFreqDist:

    def __init__(self, cond_samples=[], database=':memory:'):
        self._journal = ConditionalFreqDist()

        conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        self._sql = conn.cursor()
        self._sql.execute(
            'create table cfd(k tuple unique primary key, v dict)')

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

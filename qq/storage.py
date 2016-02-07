"""
Simple data storage functionality via Sqlite.
"""
import collections
import json
import os

import qq.common as qq


def to_serializable(obj):
    """
    Convert an object to a serializable dictionary.
    """
    if isinstance(obj, basestring):
        return obj
    if isinstance(obj, ArrayProxy):
        r = []
        for x in obj:
            r.append(to_serializable(x))
        return r
    elif isinstance(obj, ObjectProxy):
        r = dict()
        for key, value in obj.iteritems():
            r[key] = to_serializable(value)
        return r
    return obj


class ArrayProxy(collections.MutableSequence):
    """
    A proxy for a persistently stored JSON array.
    """

    def __init__(self, data, storage):
        self.data = data
        self.storage = storage

    def __delitem__(self, index):
        del self.data[index]
        self.storage.save()

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __setitem__(self, index, value):
        self.data[index] = value
        self.storage.save()

    def __repr__(self):
        return repr(self.data)

    def insert(self, index, value):
        self.data.insert(index, value)
        self.storage.save()


class ObjectProxy(collections.MutableMapping):
    """
    A proxy for a persistently stored JSON object.
    """

    def __init__(self, data, storage):
        self.data = data
        self.storage = storage

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        value = self.data[key]
        if isinstance(value, basestring):
            return value
        if isinstance(value, collections.Mapping):
            return ObjectProxy(value, self.storage)
        elif isinstance(value, collections.Sequence):
            return ArrayProxy(value, self.storage)
        return value

    def __delitem__(self, key):
        del self.data[key]
        self.storage.save()

    def __setitem__(self, key, value):
        self.data[key] = value
        self.storage.save()

    def __repr__(self):
        return repr(self.data)


class Storage(collections.MutableMapping):
    """
    Simple container for data, serialized to JSON.
    """

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(to_serializable(self.data), f, indent=2, sort_keys=True)

    def load(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w+') as f:
                f.write('{}')
        with open(self.filename, 'r') as f:
            try:
                self.data = ObjectProxy(json.load(f), self)
            except:
                self.data = ObjectProxy(dict(), self)

    def __init__(self, name):
        self.data = None
        self.name = name
        self.filename = qq.get_data_filename(self.name + '.json')
        self.load()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, item):
        keyparts = item.split('.')
        obj = self.data
        for part in keyparts:
            if part not in obj:
                return False
            obj = obj[part]
        return True

    def __getitem__(self, item):
        keyparts = item.split('.')
        obj = self.data
        for part in keyparts[:-1]:
            if part not in obj:
                raise KeyError(part)
            obj = obj[part]
        return obj[keyparts[-1]]

    def __setitem__(self, item, value):
        keyparts = item.split('.')
        obj = self.data
        for part in keyparts[:-1]:
            if part not in obj or not isinstance(obj[part], collections.Mapping):
                obj[part] = dict()
            obj = obj[part]
        obj[keyparts[-1]] = value

    def __delitem__(self, item):
        keyparts = item.split('.')
        obj = self.data
        for part in keyparts[:-1]:
            if part not in obj:
                raise KeyError(part)
            obj = obj[part]
        del obj[keyparts[-1]]

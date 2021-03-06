import redis

from rltk.record import Record
from rltk.io.adapter import KeyValueAdapter
from rltk.io.serializer import Serializer, PickleSerializer


class RedisAdapter(KeyValueAdapter):
    """
    Redis adapter.
    
    Args:
        host (str): Host address.
        serializer (Serializer, optional): The serializer used to serialize Record object. 
                                If it's None, `PickleSerializer` will be used. Defaults to None.
        key_format (str, optional): Format of key in redis. Defaults to `'{record_id}'`.
        **kwargs: Other parameters used by `redis.Redis <https://redis-py.readthedocs.io/en/latest/#redis.Redis>`_ .
    """
    def __init__(self, host, serializer: Serializer=None, key_format='{record_id}', **kwargs):
        if not serializer:
            serializer = PickleSerializer()
        self._redis = redis.Redis(host=host, **kwargs)
        self._serializer = serializer
        self._key_format = key_format
        try:
            self._get_key('test_id')
        except:
            raise ValueError('Invalid key_format.')

    #: parallel-safe
    parallel_safe = True

    def _get_key(self, record_id):
        return self._key_format.format(record_id=record_id)

    def get(self, record_id) -> Record:
        return self._serializer.loads(self._redis.get(self._get_key(record_id)))

    def set(self, record_id, record: Record):
        return self._redis.set(self._get_key(record_id), self._serializer.dumps(record))

    def __next__(self):
        # scan_iter() returns generator, keys() returns array
        for key in self._redis.scan_iter(self._get_key('*')):
            yield self._serializer.loads(self._redis.get(key))

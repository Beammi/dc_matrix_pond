import pickle
import pprint
import sys

import redis

r = redis.Redis(host="localhost", port=6379, db=0)

key = sys.argv[1]

pickled_value = r.get(key)
if not pickled_value:
    print("Fish is dead, pls refresh")
    exit(0)

deserialized_value = pickle.loads(pickled_value)


pprint.pprint(vars(deserialized_value), indent=4)

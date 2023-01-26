import pickle
import sys
import time
from dataclasses import dataclass

import redis
from logging_utils import get_logger


def current_milli_time():
    return round(time.time() * 1000)


@dataclass
class ExampleObject:
    name: str
    unit_price: float
    quantity_on_hand: int = 0


log = get_logger("redis")


def connect_to_redis(
    host="localhost", port=6379, password=None, retries=3, retry_interval=1
) -> redis.StrictRedis | None:
    for i in range(retries):
        try:
            r = redis.StrictRedis(host=host, port=port, password=password)
            if r.ping():
                log.info(f"Connected to Redis at {host}:{port}")
                return r
            else:
                raise redis.ConnectionError()
        except redis.ConnectionError as e:
            if i < retries - 1:
                log.warning(
                    f"Error connecting to Redis at {host}:{port} {e} Retrying in {retry_interval} seconds..."
                )
                time.sleep(retry_interval)
            else:
                log.warning(
                    f"Error connecting to Redis at {host}:{port} after {retries} attempts. Giving up."
                )
                return None
        except redis.RedisError as e:
            log.exception(f"Error connecting to Redis at {host}:{port} {e}")
            return None


# Fish transporter from/to redis
class FishStore:
    pass


# TODO: get address from env
r = connect_to_redis()
if not r:
    log.critical("Failed to connect to redis")
    sys.exit(1)


r.set("foo", "bar", ex=10)  # 10 seconds TTL
for key in r.scan_iter():
    print(key)

# test pickling
obj = ExampleObject(name="What else is here?", unit_price=200.22)
pickled_object = pickle.dumps(obj)
r.set("some_key", pickled_object)
unpacked_object = pickle.loads(r.get("some_key"))
log.info(unpacked_object)

# pubsub - remove expire (dead) fish
def event_handler(msg):
    try:
        key = msg["data"].decode("utf-8")
        log.info(f"Key expire event: msg: {msg}, key: {key}")
    except Exception as e:
        log.exception(f"pubsub handler error: {e}")


r.config_set("notify-keyspace-events", "Ex")
pubsub = r.pubsub()
pubsub.psubscribe(**{"__keyevent@0__:expired": event_handler})
pubsub.run_in_thread(sleep_time=0.01)

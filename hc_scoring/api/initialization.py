import time
from contextlib import contextmanager
import json

@contextmanager
def timer(title):
    t0 = time.time()
    yield
    print("{} - done in {:.0f}s".format(title, time.time() - t0))
    
def get_config_parameters(file="conf.json"):
    config = {}
    try:
        with open(file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print ("Error while opening config file", file, "error", e)
        exit()
    return config
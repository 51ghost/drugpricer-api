"""DrugPricer API — Data Pipeline with curated data"""
import time
class DataCache:
    def __init__(self, ttl=3600):
        self.cache = {}
        self.ttl = ttl
    def get(self, key):
        if key in self.cache:
            data, ts = self.cache[key]
            if time.time() - ts < self.ttl:
                return data
        return None
    def set(self, key, data):
        self.cache[key] = (data, time.time())
cache = DataCache()

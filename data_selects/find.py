import logging
import redis


from redis_lru import RedisLRU
from data_processing import db
from pymongo import errors

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)


@cache
def find_in_documents(col: str, obj: dict) -> bytes:
    """Searching for data in database documents
    with using regex matching"""
    try:
        collection = db[col]
        object_key = obj.keys()
        value = obj.get(object_key)
        fetched_data = collection.find({object_key: {"$regex": value, "$options": "i"}})
        result = ""
        for doc in fetched_data:
            doc_keys = doc.keys()
            for key in doc_keys:
                result += f"{key}: {doc.get(key)}\n"
        logging.info("Fetching data successfully") if result else None
        return result.encode("utf-8")
    except errors.PyMongoError as err:
        logging.error(f"Error while searching for data{err}")

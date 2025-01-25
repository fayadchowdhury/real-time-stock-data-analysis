import json

def deserialize(data: bytes) -> dict:
    return json.loads(data.decode('utf-8'))
import json

def serialize(data) -> bytes:
    return json.dumps(data).encode('utf-8')
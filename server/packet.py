# Provide a way to construct and deconstruct packets
# that will be sent and received

import json
import enum

class Action(enum.Enum):
    pass

class Packet:
    def __init__(self, action, *payloads):
        self.action: Action = action
        self.payloads: tuple = payloads

    def __str__(self) -> str:
        # serialize_dict = {'a': self.action.name}
        serialize_dict = {}
        for i in range(len(self.payloads)):
            serialize_dict[f'p{i}'] = self.payloads[i]
        json_obj = json.dumps(serialize_dict, separators=(',', ':'))
        return json_obj

    def __bytes__(self) -> bytes:
        return str(self).encode('utf-8')

def from_json(json_obj: str) -> Packet:
    obj_dict = json.loads(json_obj)

    action = None

    try:
        action = obj_dict.pop('a')
    except:
        pass

    payloads = obj_dict.values()


p = Packet(None, 12, 13)
print(bytes(p))
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
    except KeyError as e:
        print(f"Tried to create packet from dictionary, but there is no action. Stacktrace: {e}")

    payloads = list(obj_dict.values())
    print(payloads)

    class_name = action + "Packet"
    try:
        constructor: type = globals()[class_name]
        return constructor(*payloads)
    except KeyError as e:
        print(f"{class_name} is not a validpacket name. Stacktrace: {e}")
    except TypeError:
        print(f"{class_name} can't handle arguments {tuple(payloads)}.")


p = Packet(None, 12, 13)
from_json(str(p))
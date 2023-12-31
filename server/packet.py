import json
import enum

class Action(enum.Enum):
    # enum.auto() allows to automatically assign unique values to each member
    Chat = enum.auto()
    Ok = enum.auto()
    Deny = enum.auto()
    Register = enum.auto()
    Login = enum.auto()


class Packet:
    def __init__(self, action: Action, *payloads):
        self.action: Action = action
        self.payloads: tuple = payloads

    def __str__(self) -> str:
        serialize_dict = {'a': self.action.name}
        for i in range(len(self.payloads)):
            serialize_dict[f'p{i}'] = self.payloads[i]
        json_obj = json.dumps(serialize_dict, separators=(',', ':'))
        return json_obj

    def __bytes__(self) -> bytes:
        return str(self).encode('utf-8')

class ChatPacket(Packet):
    def __init__(self, message: str):
        super().__init__(Action.Chat, message)

class OkPacket(Packet):
    def __init__(self):
        super().__init__(Action.Ok)

class DenyPacket(Packet):
    def __init__(self, reason: str):
        super().__init__(Action.Deny, reason)

class LoginPacket(Packet):
    def __init__(self, username: str, password: str):
        super().__init__(Action.Login, username, password)

class RegisterPacket(Packet):
    def __init__(self, username: str, password: str):
        super().__init__(Action.Login, username, password)



def from_json(json_obj: str) -> Packet:
    obj_dict = json.loads(json_obj)

    action = None

    try:
        action = obj_dict.pop('a')
    except KeyError as e:
        print(f"Tried to create packet from dictionary, but there is no action. Stacktrace: {e}")

    payloads = list(obj_dict.values())

    class_name = action + "Packet"
    try:
        constructor: type = globals()[class_name]
        return constructor(*payloads)
    except KeyError as e:
        print(f"{class_name} is not a validpacket name. Stacktrace: {e}")
    except TypeError:
        print(f"{class_name} can't handle arguments {tuple(payloads)}.")


# p = ChatPacket("12")
# print(str(p))
import queue
import packet
import models
from autobahn.twisted.websocket import WebSocketServerProtocol

# We need protocol class to specify the behaviour of the server
class GameServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self._packet_queue: queue.Queue[tuple['GameServerProtocol', packet.Packet]] = queue.Queue()
        self._state: callable = self.PLAY
        self._user: models.User = None

    # States
    def PLAY(self, sender: 'GameServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Chat:
            if sender == self:
                self.broadcast(p, exclude_self=True)
            else:
                self.send_client(p)

    def LOGIN(self, sender: 'GameServerProtocol', p: packet.Packet):
        if p.action == packet.Action.Login:
            username, password = p.payloads
            if models.User.objects.filter(username=username, password=password).exists():
                self._user = model.User.objects.get(username=username)
                self.send_client(packet.OkPacket())
                self._state = self.PLAY
            else:
                self.send_client(packet.DenyPacket("Username or password incorrect"))

        elif p.action == packet.Action.Register:
            username, password = p.payloads
            if models.User.objects.filter(username=username).exists():
                self.send_client(packet.DenyPacket("This username already exists"))
            else:
                user = models.User(username=username, password=password)
                user.save()
                self.send_client(packet.OkPacket())


    def tick(self):
        # Process the next packet in the queue
        if not self._packet_queue.empty():
            s, p = self._packet_queue.get()
            self._state(s, p)

    # broadcast packet to everyone
    def broadcast(self, p: packet.Packet, exclude_self: bool = False):
        for other in self.factory.players:
            if other == self and exclude_self:
                continue
            other.onPacket(self, p)

    # Override
    def onPacket(self, sender: 'GameServerProtocol', p: packet.Packet):
        self._packet_queue.put((sender, p))
        print(f"Queued packet: {p}. Action = {p.action}")

    # Override
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    # Override
    def onOpen(self):
        print(f"Websocket connection open.")
        self._state = self.LOGIN

    # Override
    def onClose(self, wasClean, code, reason):
        self.factory.players.remove(self)
        print(f"Websocket connection closed {'cleanly' if wasClean else 'unexpectedly'} with code {code}: {reason}")

    # Override
    # Called when a new WebSocket message was received
    def onMessage(self, payload, isBinary):
        # payload is a Python byte string. We docode it into a Python string.
        # Autobahn validates bytes for being valid UTF8
        decoded_payload = payload.decode('utf-8')

        try:
            p: packet.Packet = packet.from_json(decoded_payload)
        except Exception as e:
            print(f"Could not load message as packet: {e}. Message was: {payload.decode('utf-8')}")

        self.onPacket(self, p)

    # Send message directly to a client without broadcasting to other protocols
    def send_client(self, p: packet.Packet):
        b = bytes(p)
        self.sendMessage(b)
import queue
import packet
from autobahn.twisted.websocket import WebSocketServerProtocol

# We need protocol class to specify the behaviour of the server
class GameServerProtocol(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self._packet_queue: queue.Queue[tuple['GameServerProtocol', packet.Packet]] = queue.Queue()
        self._state: callable = None

    # States
    def PLAY(self, sender: 'GameServerProtocol', p: packet.Packet):
        pass

    def tick(self):
        #Process the next packet in the queue
        if not self._packet_queue.empty():
            s, p = self._packet_queue.get()
            self._state(s, p)

    # broadcast packet to everyone
    def broadcast(self, p: packet.Packet, exclude_self: bool = False):
        for other in self.factory.players:
            if other == self and exclude_self:
                continue
            other.onPacket(self, p)

    def onPacket(self, sender: 'GameServerProtocol', p: packet.Packet):
        self._packet_queue.put((sender, p))
        print(f"Queued packet: {p}")

    # Override
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    # Override
    def onOpen(self):
        print(f"Websocket connection open.")
        self._state = self.PLAY

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
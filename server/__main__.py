import sys
import protocol
from twisted.python import log
from twisted.internet import reactor, task
from autobahn.twisted.websocket import WebSocketServerFactory


class GameFactory(WebSocketServerFactory):
    def __init__(self, hostname: str, port: int):
        self.protocol = protocol.GameServerProtocol
        super().__init__(f"ws://{hostname}:{port}")

        self.players: set[protocol.GameServerProtocol] = set()

        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / 20)  # 20 times per second

    def tick(self):
        for player in self.players:
            player.tick()

    # Override
    def buildProtocol(self, addr):
        protocol = super().buildProtocol(addr)
        self.players.add(protocol)
        return protocol

if __name__ == "__main__":
    log.startLogging(sys.stdout)

    PORT: int = 8082
    factory = GameFactory("127.0.0.1", PORT)

    reactor.listenTCP(PORT, factory)
    reactor.run()

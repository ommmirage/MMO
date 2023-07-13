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

        # tick() will be called 20 times per second
        tickloop = task.LoopingCall(self.tick)
        tickloop.start(1 / 20)

    def tick(self):
        for player in self.players:
            player.tick()

    # Override
    # When a new connection is made to the server, the Twisted networking framework
    # automatically calls this method passing the connection's address.
    def buildProtocol(self, addr):
        print(addr)
        protocol = super().buildProtocol(addr)
        self.players.add(protocol)
        return protocol


if __name__ == "__main__":
    log.startLogging(sys.stdout)

    PORT: int = 8081
    # If you want your WebSocket server to be accessible from any IP address associated with your machine
    factory = GameFactory("0.0.0.0", PORT)

    # Start a server using the factory, listening on TCP
    reactor.listenTCP(PORT, factory)
    reactor.run()

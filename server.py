import select
import socket
import sys
import random
import struct

NUMBER = random.randint(1,100)
print(NUMBER)
EQUALS = '='
LESS = '<'
GREATER = '>'
YES = 'I'
NO = 'N'
OUT = 'K'
END = 'V'
WIN = 'Y'

class SimpleTCPSelectServer:
    def __init__(self, gameObj, addr='localhost', port=10001, timeout=1):
        self.server = self.setupServer(addr, port)
        # Sockets from which we expect to read
        self.inputs = [self.server]
        # Wait for at least one of the sockets to be ready for processing
        self.timeout = timeout
        self.gameObj = gameObj
        self.packer = struct.Struct("ci")

    def setupServer(self, addr, port):
        # Create a TCP/IP socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the port
        server_address = (addr, port)
        server.bind(server_address)

        # Listen for incoming connections
        server.listen(5)
        return server

    def handleNewConnection(self, sock):
        # A "readable" server socket is ready to accept a connection
        connection, client_address = sock.accept()
        connection.setblocking(0)  # or connection.settimeout(1.0)
        self.inputs.append(connection)

    def handleDataFromClient(self, sock):
        raw_data = sock.recv(self.packer.size)
        if raw_data:
            data = self.packer.unpack(raw_data)
            # print(data)
            ans = self.gameObj.handleUser(data[0].decode(), data[1])
            ans = self.packer.pack(ans.encode(), 0)
            sock.sendall(ans)  # itt visszaküldhetünk valamit
            pass
        else:
            # Interpret empty result as closed connection
            # Stop listening for input on the connection
            self.inputs.remove(sock)
            sock.close()

    def handleInputs(self, readable):
        for sock in readable:
            if sock is self.server:
                self.handleNewConnection(sock)
            else:
                self.handleDataFromClient(sock)

    def handleExceptionalCondition(self, exceptional):
        for sock in exceptional:
            # Stop listening for input on the connection
            self.inputs.remove(sock)
            sock.close()

    def handleConnections(self):
        while self.inputs:
            try:
                readable, writable, exceptional = select.select(
                    self.inputs, [], self.inputs, self.timeout)

                if not (readable or writable or exceptional):
                    continue

                self.handleInputs(readable)
                self.handleExceptionalCondition(exceptional)
            except KeyboardInterrupt:
                # print("A szerver leáll")
                for c in self.inputs:
                    c.close()
                self.inputs = []


class Game:
    def __init__(self, number):
        self.number = number
        self._finished = False

    def handleUser(self, operation, number):
        if self._finished:
            # print('already finished')
            return END

        if operation == EQUALS:
            return self.handleGuess(number)
        else:
            return self.handleQuetsion(operation, number)

    def handleGuess(self, number):
        if self.number == number:
            self._finished = True
            # print('finished')
            return WIN
        else:
            return OUT

    def handleQuetsion(self, operation, number):
        if operation == LESS:
            if number < self.number: return NO
            if number > self.number: return YES

        elif operation == GREATER:
            if number < self.number: return YES
            if number > self.number: return NO

        return NO

    @property
    def finished(self):
        return self._finished


if __name__ == '__main__':
    game = Game(NUMBER)
    if len(sys.argv) == 3:
        simpleTCPSelectServer = SimpleTCPSelectServer(game, sys.argv[1], int(sys.argv[2]))
    else:
        simpleTCPSelectServer = SimpleTCPSelectServer(game)
   
    simpleTCPSelectServer.handleConnections()
    
    


import sys
import socket
import random
import struct
import time

server_addr = sys.argv[1]
server_port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((server_addr, server_port))

packer = struct.Struct('ci')

EQUALS = '='
LESS = '<'
GREATER = '>'
YES = 'I'
NO = 'N'
OUT = 'K'
END = 'V'
WIN = 'Y'
BOTTOM = 1
TOP = 100

def ask(number):
    # print("asking", number)
    sock.sendall(packer.pack(b'>', number))
    msg = sock.recv(packer.size)
    parsed_msg = packer.unpack(msg)
    return parsed_msg[0].decode()

def guess(number):
    # print("guessing", number)
    sock.sendall(packer.pack(b'=', number))
    msg = sock.recv(packer.size)
    parsed_msg = packer.unpack(msg)
    return parsed_msg[0].decode()


catalog_is_good = True
while catalog_is_good:
    if TOP == BOTTOM:
        ans = guess(TOP)
    else:
        middle = int((TOP + BOTTOM) / 2)
        ans = ask(middle)

    if (ans == END) or (ans == WIN) or (ans == OUT):
        # print("done")
        break

    if ans == NO:
        TOP = middle

    elif ans == YES:
        BOTTOM = middle + 1



# for i in range(10):
# 	random_index = random.randint(1, 30)
# 	print("Üzenet: %d" % (random_index))
# 	sock.sendall(str(random_index).encode())
# 	msg = sock.recv(packer.size)
# 	parsed_msg = packer.unpack(msg)
# 	print("Kapott eredmény: fib(%d):%d (%d alkalommal kérték)" %
# 	      (random_index, parsed_msg[0], parsed_msg[1]))
# 	time.sleep(2)


sock.close()

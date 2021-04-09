import socketserver
import sys
import random
import containers
from http_handler import RequestHandler

"""resources"""
# TCP socket setup source documentation https://docs.python.org/3/library/socketserver.html
# String methods and manipulations https://docs.python.org/3/library/stdtypes.html
"""resources"""


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):

        sys.stdout.flush()
        my_handler = RequestHandler()
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(2000).strip()
        send_data = my_handler.handle(self, self.data)
        sys.stdout.flush()
        #print("SENDING.... ", send_data, "/n")
        self.request.sendall(send_data)  # data is already in bytes so no need to encode


if __name__ == "__main__":
    port = "800"
    port += str(random.randint(0, 9))  # Temporary so I can just restart without worrying about the port
    HOST, PORT = "0.0.0.0", int(port)

    # Create the server, binding to localhost on port
    print("(address will not work when running in docker) Server started at -> ", "http://" + HOST + ":" + str(PORT) + "\n")
    # this resets the home page to its original state fro when there server first starts up
    reset = open("../src/sample_page/default_page.html", "r")
    read_in = reset.read()
    home_page = open("../src/sample_page/index.html", "w")
    home_page.write(read_in)
    reset.close()
    home_page.close()

    sys.stdout.flush()
    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

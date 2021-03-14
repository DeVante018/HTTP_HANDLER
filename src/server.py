import socketserver
import sys
from http_handler import RequestHandler

"""resources"""
# TCP socket setup source documentation https://docs.python.org/3/library/socketserver.html
# String methods and manipulations https://docs.python.org/3/library/stdtypes.html
"""resources"""


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        sys.stdout.flush()
        my_handler = RequestHandler()
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        all_headers_map = my_handler.parser(self.data)
        send_data = my_handler.process(all_headers_map)
        sys.stdout.flush()
        # print("\n\n\n\n\n----sending response...----\n\n\n\n\n")
        # print(send_data)
        # print("\n\n\n\n\n----################-------\n\n\n\n\n")
        self.request.sendall(send_data)  # data is already in bytes so no need to encode


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000

    # Create the server, binding to localhost on port
    print("(address will not work when running in docker) Server started at -> ", "http://" + HOST + ":" + str(PORT) + "\n")
    sys.stdout.flush()
    with socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

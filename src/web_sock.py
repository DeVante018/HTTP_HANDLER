import hashlib
import base64


def upgrade_connection(hash_key):
    pre = hash_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    my_hash = hashlib.sha1(pre.encode()).hexdigest()  # Hex so I can encode to base64
    encode = base64.b64encode(bytes.fromhex(my_hash))
    response = "/HTTP/1.1 101\r\n"
    response += "Connection: Upgrade\r\n"
    response += "Upgrade: websocket\r\n"
    response += "Sec-WebSocket-Accept: "
    response = response.encode()
    response += encode + bytes('\r\n\r\n', 'utf8')
    return response

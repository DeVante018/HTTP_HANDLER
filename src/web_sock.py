import pymongo
from bitstring import BitArray
from containers import Statics
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


def show_frame(data):
    count = 0
    bits_array = []
    #print("\n---------frame---------\n")
    data = BitArray(data)
    build_byte = ""
    count = 1
    for bits in data.bin:
        build_byte += str(bits)
        if count == 8:
            count = 1
            bits_array.append(build_byte)
            build_byte = ""
        else:
            count += 1
    level = 0
    while level < len(bits_array) - 1:
        if level + 3 < len(bits_array):
            #(bits_array[level], bits_array[level + 1], bits_array[level + 2], bits_array[level + 3])
            level = level + 4

        elif level + 2 < len(bits_array):
            #print(bits_array[level], bits_array[level + 1], bits_array[level + 2])
            level = level + 3

        else:
            #print(bits_array[level], bits_array[level + 1])
            level = level + 2
    #print("\n---------frame---------\n")
    return bits_array


def build_frame(data_chunks):

    frame = 129
    frame = frame.to_bytes(1, 'big')  # first 8 bytes are guaranteed this for this assignment
    data_in_bytes = bytes()
    for _bytes in data_chunks:
        integer_rep = int(_bytes, 2)
        data_in_bytes += integer_rep.to_bytes(1, 'big')
        #print(integer_rep)
        # print(integer_rep.to_bytes(2, 'big'))
    # print("data in bytes: ", data_in_bytes)
    data_in_bytes = data_in_bytes.replace(b"&", b"&amp;")
    data_in_bytes = data_in_bytes.replace(b"<", b"&lt;")
    data_in_bytes = data_in_bytes.replace(b">", b"&gt;")
    payload_len = len(data_in_bytes)
    # print(payload_len)
    if payload_len < 126:
        frame += payload_len.to_bytes(1, 'big')
    elif 126 <= payload_len < 65536:
        full = 126
        frame += full.to_bytes(1, 'big')
        new_len = format(payload_len, '016b')
        first_num = ""
        second_num = ""
        for num in range(16):
            if num < 8:
                first_num += new_len[num]
            else:
                second_num += new_len[num]
        first_num = int(first_num, 2)
        second_num = int(second_num, 2)
        frame += first_num.to_bytes(1, 'big')
        frame += second_num.to_bytes(1, 'big')
    else:
        print("This wouldn't even work because my recv buffer isn't big enough to handle this")
    frame += data_in_bytes
    # print(frame)
    return frame


def read_socket(skt):
    # Fin=1 opcode=1 MASK=1

    pay_length = 127
    while True:
        mask_idx = 0
        mask_block = []
        unmasked_data = []
        try:
            data = skt.request.recv(2000)
            frame = show_frame(data)
            check_fin = int(frame[0][0], base=2) & 1
            check_opcode = int(frame[0][7], base=2) & 1
            # print("FIN: ", check_fin)
            # print("OPCODE: ", check_opcode)
            if check_fin != 1:
                # print("FIN NOT 1: socket closed...")
                return

            if check_opcode != 1:
                # print("OPCODE NOT 1: socket closed...")
                return

            check_payload = int(frame[1], base=2) & pay_length
            if check_payload < 126:
                mask_idx = 2
                # print("126 > PAYLOAD: ", check_payload)

            elif check_payload == 126:
                nxt_16 = int(frame[2] + frame[3], base=2)
                check_payload = nxt_16
                mask_idx = 4
                # print("126 = PAYLOAD: ", check_payload)

            elif check_payload == 127:
                nxt_64 = ""
                for binary in frame[2:9]:
                    nxt_64 = binary
                check_payload = int(nxt_64, base=2)
                mask_idx = 10
                # print("127 = PAYLOAD: ", check_payload)

            else:
                # print("Payload length error...")
                return

            # put 4 bytes of the mask inside of the an array, each byte being at one idx
            for idx in range(mask_idx, mask_idx + 4):
                mask_block.append(frame[idx])
            # print("MASK_BYTES: ", mask_block)
            start_data = mask_idx + 4
            four_byte_chunk = []
            data_in_bits = ""
            for _data in frame[start_data:]:
                four_byte_chunk.append(_data)
                if len(four_byte_chunk) == 4:
                    for x in range(4):
                        # print("DEBUG-------------------")
                        chunk_byte = int(four_byte_chunk[x], base=2)
                        mask_byte = int(mask_block[x], base=2)
                        xor = chunk_byte ^ mask_byte
                        # print("CHUNK: ", bin(chunk_byte))
                        # print("MASK: ", bin(mask_byte))
                        # print("RESULT ", bin(xor))
                        # print("DEBUG-------------------\n")
                        unmasked_data.append(format(xor, "08b"))  # putting each byte in an array
                        data_in_bits += format(xor, "08b")
                    four_byte_chunk = []
            if len(four_byte_chunk) != 0:
                idx = 0
                for remainder in four_byte_chunk:
                    chunk_byte = int(remainder, base=2)
                    mask_byte = int(mask_block[idx], base=2)
                    xor = chunk_byte ^ mask_byte
                    # print("CHUNK: ", bin(chunk_byte))
                    # print("MASK: ", bin(mask_byte))
                    # print("RESULT ", bin(xor))
                    # print("DEBUG-------------------\n")
                    unmasked_data.append(format(xor, "08b"))  # putting each byte in an array
                    data_in_bits += format(xor, "08b")
                    idx += 1
                # print(data_in_bits)
            send = build_frame(unmasked_data)
            Statics.chat.insert_one({"message": send})
            for all_connection in Statics.server_web_sockets:
                all_connection.sendall(send)
        except:
            print("Socket closed on error...")
            return

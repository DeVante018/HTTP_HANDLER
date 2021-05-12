from containers import Statics
from paths import Paths
from on_get import Get
from on_post import Post


class RequestHandler:
    path_obj = Paths()
    get_handler = Get()
    post_handler = Post()

    def handle(self, socket, request) -> bytes:
        headers_map = {}
        byte_array = bytearray(request)
        split_array = byte_array.split(bytes("\r\n\r\n", encoding="utf8"))
        split_len = len(split_array)
        sanitize = split_array[0].decode()  # change this to handle multi part form data
        split_data = sanitize.splitlines()

        for x in request.splitlines():
            print(x)
        print("\n")

        first_header = split_data[0].split(" ")
        path = first_header[1]
        request_type = first_header[0].replace(" ", "")
        version = first_header[2]

        # will get more headers later if I need them
        headers_map["request_type"] = request_type  # should be GET or POST
        headers_map["path"] = path  # path searched for
        headers_map["version"] = version  # HTTP version the browser is using
        i = 0
        for headers in split_data:
            if i != 0:
                header_split = headers.split(":")
                headers_map[header_split[0]] = header_split[1].replace(" ", "")
            i += 1

        # print(headers_map)
        return_bytes = bytes
        has_cookie = False
        parse_cookie = []
        Statics.token = ""
        for keys in headers_map:
            if str(keys) == 'Cookie':
                has_cookie = True
        if has_cookie:
            parse_cookie = headers_map['Cookie']
            parse_cookie = parse_cookie.split(";")
            length = len(parse_cookie)
        else:
            length = 0
        print("LENGTH____", length)
        if length == 2:
            Statics.current_cookie = parse_cookie[1]
            Statics.token = parse_cookie[0].split('=')
            parse_cookie = parse_cookie[1].split("=")
            if len(Statics.token) > 1:
                Statics.token = Statics.token[1]
            else:
                Statics.token = ""
        elif length == 3:
            auth_cookie = parse_cookie[2].split("=")
            Statics.token = auth_cookie[1]
        else:
            if len(parse_cookie) != 0 and parse_cookie[0][0] == 'i':
                # this is firefox doing w.e tf it wants
                parse_cookie = parse_cookie[0].split("=")
                if len(parse_cookie) > 1:
                    Statics.current_cookie = parse_cookie[1]
                else:
                    Statics.current_cookie = ""
        if headers_map["request_type"] == "GET":
            return_bytes = self.get_handler.process(headers_map, socket)
        elif headers_map["request_type"] == "POST":
            return_bytes = self.post_handler.process(socket, headers_map, split_array, split_len)
        # process the request based on what it is
        return return_bytes

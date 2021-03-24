from paths import Paths
from on_get import Get
from on_post import Post

# when running on my machine
# /Users/devantefrederick/IdeaProjects/HTTP_HANDLER/src/sample_page/index.html
# /Users/devantefrederick/IdeaProjects/HTTP_HANDLER/src/sample_page/functions.js
# /Users/devantefrederick/IdeaProjects/HTTP_HANDLER/src/sample_page/style.css
# /Users/devantefrederick/IdeaProjects/HTTP_HANDLER/src/sample_page/utf.txt
# /Users/devantefrederick/IdeaProjects/HTTP_HANDLER/src/sample_page/image/flamingo.jpg


class RequestHandler:
    path_obj = Paths()
    get_handler = Get()
    post_handler = Post()

    def handle(self, request) -> bytes:
        headers_map = {}
        byte_array = bytearray(request)
        split_array = byte_array.split(bytes("\r\n\r\n", encoding="utf8"))
        sanitize = split_array[0].decode()  # change this to handle multi part form data
        split_data = sanitize.splitlines()

        for x in request.decode().splitlines():
            print(x)
        print("\n")

        first_header = split_data[0].split(" ")
        path = first_header[1]
        request_type = first_header[0].replace(" ", "")
        version = first_header[2]

        # will get more headers later if I need them
        headers_map["request_type"] = request_type  # should be GET or POST
        headers_map["path"] = path  # path searched for
        headers_map["version"] = version # HTTP version the browser is using
        i = 0
        for headers in split_data:
            if i != 0:
                header_split = headers.split(":")
                headers_map[header_split[0]] = header_split[1].replace(" ", "")
            i += 1

        return_bytes = bytes

        if headers_map["request_type"] == "GET":
            return_bytes = self.get_handler.process(headers_map)
        elif headers_map["request_type"] == "POST":
            return_bytes = self.post_handler.process(headers_map, split_array)
        # process the request based on what it is
        return return_bytes

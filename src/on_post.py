import paths


def build_response_comment(p_obj, content_arr):
    template = open("/Users/devantefrederick/IdeaProjects/HTTP_HANDLER/src/sample_page/index.html", "r")
    template = template.readlines()
    new_template = ""
    comment_section = False
    html_p = "<p style=" + "text-align:left;" + ">~</p>"
    for x in template:
        # print(x)
        if comment_section:
            for commenter in content_arr:
                line = str(commenter[0].decode()) + " has submitted a comment of: " + str(commenter[1].decode())
                paragraph = html_p.replace("~", line)
                new_template += paragraph

        if x == '<h1>Comments</h1>\n':
            comment_section = True
        else:
            comment_section = False

        new_template += x
    # print(new_template)

    response_bytes = bytes(new_template, "utf8")
    build_str = ""
    build_str += p_obj.http_version + " " + p_obj.ok
    build_str += p_obj.slash_rn
    build_str += p_obj.content_length
    build_str += str(len(response_bytes))
    build_str += p_obj.slash_rn
    build_str += p_obj.content_text_html
    build_str += p_obj.slash_rn
    build_str += p_obj.no_sniff
    build_str += p_obj.slash_rn + p_obj.slash_rn
    convert_bytes = bytes(build_str, encoding='utf8')
    convert_bytes += response_bytes
    return convert_bytes


def post_comment(dictionary, byt_array):
    sls_rn = bytes("\r\n", "utf8")
    boundary = dictionary['Content-Type'].split("=")
    boundary = "--" + str(boundary[1])
    # print(boundary)
    byte_block = bytes("", "utf8")
    total_data = 0
    received_info = []

    for data in byt_array[1:]:
        # print(data)
        byte_block += bytes(data)
        total_data += len(bytes(data))
    mult_part = byte_block.split(bytes(boundary, "utf8"))
    print("\n")

    idx = 1
    sanitizing = True
    while sanitizing:
        data = mult_part[idx]
        # print(data)
        if data.decode() == "--":
            sanitizing = False
        else:
            parsing = data.replace(sls_rn, bytes("", "utf8"))
            # print("###########", parsing)
            parsing = parsing.split(bytes(":", "utf8"))
            # print("###########", parsing)
            parsing = parsing[1].split(bytes(";", "utf8"))
            # print("###########", parsing)
            parsing = parsing[1].split(bytes("\"", "utf8"))
            # print("###########", parsing)
            received_info.append(parsing[2])
        idx += 1
    return received_info


def upload_image(self_obj, headers, parse_array, socket, split_len):
    boundary = headers['Content-Type'].split("=")
    in_boundary = "--" + boundary[1]
    encoded = bytes(in_boundary, "utf8")
    boundary = boundary[1].replace("-", "")
    boundary += "--"
    boundary_bytes = bytes(boundary, encoding="utf8")
    received = bytes("", encoding="utf8")
    caption = ""
    # print(boundary_bytes)
    print("\n--------------POST REQUEST--------------\n")
    for x in parse_array[1:]:
        print("###############", x)
    print("\n--------------POST REQUEST--------------\n")
    read_all_bytes = -1
    if split_len < 2:
        print("###########", split_len)
        incoming_data = socket.request.recv(1024)
        incoming_data = incoming_data.split(bytes("\r\n\r\n", "utf8"))
        received = incoming_data[1]
    else:
        if split_len >= 2:
            for x in parse_array[2:]:
                received += x

    while read_all_bytes == -1:
        incoming_data = socket.request.recv(1024).strip()
        read_all_bytes = incoming_data.find(boundary_bytes)
        if read_all_bytes != -1:
            split_data = incoming_data.split(bytes("\r\n", "utf8"))
            incoming_data = bytes("", "utf8")
            stop_concat = False
            for remaining_bytes in split_data:
                if remaining_bytes == encoded:
                    stop_concat = True
                if not stop_concat:
                    incoming_data += remaining_bytes
            caption = split_data[len(split_data)-2]
        received += incoming_data
        # print(incoming_data)
    print("Done reading...")
    print("Uploaded image with caption: " + caption.decode())
    print("FULL DATA: ", received)

    self_obj.images.append([caption.decode(), received])
    return bytes("Good response", encoding="utf8")


def error(p_obj):
    response = "given path is not supported"
    response_bytes = bytes(response, "utf8")
    build_str = ""
    build_str += p_obj.http_version + " " + p_obj.ok
    build_str += p_obj.slash_rn
    build_str += p_obj.content_length
    build_str += str(len(response_bytes))
    build_str += p_obj.slash_rn
    build_str += p_obj.content_text_plain
    build_str += p_obj.slash_rn
    build_str += p_obj.no_sniff
    build_str += p_obj.slash_rn + p_obj.slash_rn
    #convert_bytes = bytes(build_str, encoding='utf8')
    #convert_bytes += response_bytes
    build_str += response
    return bytes(build_str, encoding="utf8")


class Post:
    archive = []
    images = []
    file_paths = paths.Paths()
    return_response = bytes("", "utf8")

    def process(self, socket, dictionary: dict, byte_array_response, split_len):
        # this is a post request so we need to be very careful on parsing this
        if dictionary["path"] == "/comment":
            received_info = post_comment(dictionary, byte_array_response)
            self.archive.append(received_info)
            return_response = build_response_comment(self.file_paths, self.archive)
        elif dictionary["path"] == "/image-upload":
            return_response = upload_image(self, dictionary, byte_array_response, socket, split_len)
        else:
            return_response = error(self.file_paths)

        return return_response

import paths


def build_response(p_obj, content_arr):
    response = str(content_arr[0].decode()) + " has submitted a comment: " + str(content_arr[1].decode())
    response_bytes = bytes(response, "utf8")
    build_str = ""
    build_str += p_obj.http_version + " " + p_obj.ok
    build_str += p_obj.slash_rn
    build_str += p_obj.content_length
    build_str += str(len(bytes(response_bytes)))
    build_str += p_obj.slash_rn
    build_str += p_obj.content_text_plain
    build_str += p_obj.slash_rn
    build_str += p_obj.no_sniff
    build_str += p_obj.slash_rn + p_obj.slash_rn
    convert_bytes = bytes(build_str, encoding='utf8')
    convert_bytes += response_bytes
    return convert_bytes


class Post:
    archive = []
    file_paths = paths.Paths()

    def process(self, dictionary: dict, byte_array_response):
        # this is a post request so we need to be very careful on parsing this
        sls_rn = bytes("\r\n", "utf8")
        boundary = dictionary['Content-Type'].split("=")
        boundary = "--" + str(boundary[1])
        # print(boundary)
        content_length = dictionary['Content-Length']
        byte_block = bytes("", "utf8")
        total_data = 0
        received_info = []

        for data in byte_array_response[1:]:
            print(data)
            byte_block += bytes(data)
            total_data += len(bytes(data))
        mult_part = byte_block.split(bytes(boundary, "utf8"))
        print("\n")

        idx = 1
        sanitizing = True
        while sanitizing:
            data = mult_part[idx]
            print(data)
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

        self.archive.append(received_info)
        return build_response(self.file_paths, received_info)

import paths


def build_response_comment(p_obj, content_arr):
    template = open("/Users/devantefrederick/IdeaProjects/HTTP_HANDLER/src/sample_page/index.html", "r")
    template = template.readlines()
    new_template = ""
    comment_section = False
    html_p = "<p style=" + "text-align:left;" + ">~</p>"
    for x in template:
        print(x)
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
    print(new_template)

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
    convert_bytes = bytes(build_str, encoding='utf8')
    convert_bytes += response_bytes
    return convert_bytes


class Post:
    archive = []
    file_paths = paths.Paths()
    return_response = bytes("", "utf8")

    def process(self, dictionary: dict, byte_array_response):
        # this is a post request so we need to be very careful on parsing this
        if dictionary["path"] == "/comment":
            sls_rn = bytes("\r\n", "utf8")
            boundary = dictionary['Content-Type'].split("=")
            boundary = "--" + str(boundary[1])
            # print(boundary)
            content_length = dictionary['Content-Length']
            byte_block = bytes("", "utf8")
            total_data = 0
            received_info = []

            for data in byte_array_response[1:]:
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
            self.archive.append(received_info)
            return_response = build_response_comment(self.file_paths, self.archive)
        else:
            return_response = error(self.file_paths)

        return return_response

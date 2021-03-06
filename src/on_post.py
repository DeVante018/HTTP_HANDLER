import sys

import Authentication
import paths
import bcrypt
from strgen import StringGenerator as SG
from containers import Statics


def build_response_comment(p_obj, content_arr):
    template = open("../src/sample_page/default_page.html", "r")
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
        f = open("../src/sample_page/index.html", "w")
        f.write(new_template)
    # print(new_template)
    return good(p_obj)


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
        # print("IDX", idx)
        sys.stdout.flush()
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
    # print("LENGTH--------LENGTH")
    # print(headers['Content-Length'])
    # print("LENGTH--------LENGTH")

    boundary = headers['Content-Type'].split("=")
    in_boundary = "--" + boundary[1]
    encoded = bytes(in_boundary, "utf8")
    boundary = boundary[1].replace("-", "")
    boundary += "--"
    boundary_bytes = bytes(boundary, encoding="utf8")
    received = bytes("", encoding="utf8")
    caption = ""
    # print(boundary_bytes)
    # print("\n--------------POST REQUEST--------------\n")
    # for x in parse_array[1:]:
    # print("###############", x)
    # print("\n--------------POST REQUEST--------------\n")
    read_all_bytes = -1
    if split_len < 2:
        # print("###########", split_len)
        incoming_data = socket.request.recv(1024)
        incoming_data = incoming_data.split(bytes("\r\n\r\n", "utf8"))
        received = incoming_data[1]
    else:
        if split_len >= 2:
            for x in parse_array[2:]:
                received += x

    while read_all_bytes == -1:
        incoming_data = socket.request.recv(1024)
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
            caption = split_data[len(split_data) - 3]

        received += incoming_data
        # print(incoming_data)
    # print("FULL DATA: ", received)
    # print("Done reading...")
    # print("Uploaded image with caption: " + caption.decode())
    caption = caption.replace(b"&", b"&amp;")
    caption = caption.replace(b"<", b"&lt;")
    caption = caption.replace(b">", b"&gt;")
    img_name = "image" + str(self_obj.upload_num) + ".jpg"

    Statics.captions_images.append([caption.decode(), img_name])

    self_obj.images.append([caption.decode(), received])
    w = open("../src/sample_page/image/image" + str(
        self_obj.upload_num) + ".jpg", "wb")
    self_obj.upload_num += 1
    w.write(received)
    # return test_recieved_image(p, received)
    return good(paths.Paths())


def good(p_obj):
    build_str = ""
    build_str += p_obj.http_version + " " + p_obj.redirect
    build_str += p_obj.slash_rn
    build_str += "Location: "
    build_str += "/"
    return bytes(build_str, encoding="utf8")


def test_recieved_image(p_obj, array):
    build_str = ""
    build_str += p_obj.http_version + " " + p_obj.ok
    build_str += p_obj.slash_rn
    build_str += p_obj.content_length
    build_str += str(len(array))
    build_str += p_obj.slash_rn
    build_str += p_obj.content_image_jpg
    build_str += p_obj.slash_rn
    build_str += p_obj.no_sniff
    build_str += p_obj.slash_rn_rn
    convert_bytes = bytes(build_str, encoding='utf8')
    convert_bytes += array
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
    # convert_bytes = bytes(build_str, encoding='utf8')
    # convert_bytes += response_bytes
    build_str += response
    return bytes(build_str, encoding="utf8")


def security_check(array):

    array[0] = array[0].replace(b"&", b"&amp;")
    array[0] = array[0].replace(b"<", b"&lt;")
    array[0] = array[0].replace(b">", b"&gt;")
    array[1] = array[1].replace(b"&", b"&amp;")
    array[1] = array[1].replace(b"<", b"&lt;")
    array[1] = array[1].replace(b">", b"&gt;")
    return array


class Post:
    archive = []
    images = []
    file_paths = paths.Paths()
    upload_num = 1
    return_response = bytes("", "utf8")

    def process(self, socket, dictionary: dict, byte_array_response, split_len):
        # this is a post request so we need to be very careful on parsing this
        if dictionary["path"] == "/comment":
            received_info = post_comment(dictionary, byte_array_response)
            received_info = security_check(received_info)
            self.archive.append(received_info)
            return_response = build_response_comment(self.file_paths, self.archive)

        elif dictionary["path"] == "/image-upload":
            return_response = upload_image(self, dictionary, byte_array_response, socket, split_len)

        elif dictionary['path'] == "/signup_user":
            submission = post_comment(dictionary, byte_array_response)
            username = submission[0].decode()
            password = submission[1]
            valid = Authentication.check_password(password.decode())
            if valid:
                salt = bcrypt.gensalt()
                _hash = bcrypt.hashpw(password, salt)
                Statics.usr_pwd.insert_one({"username": username, "password": _hash})
                return good(self.file_paths)
            else:
                return Authentication.invalid_password()

        elif dictionary['path'] == "/signin_user":
            p = self.file_paths
            submission = post_comment(dictionary, byte_array_response)
            username = submission[0].decode()
            password = submission[1]
            get_user = Statics.usr_pwd.find({}, {'username', 'password'})

            response = ""
            response += p.http_version + " " + p.ok
            response += p.slash_rn
            response += p.content_text_html
            response += p.slash_rn
            response += p.content_length
            is_valid = False
            for users in get_user:
                if users['username'] == username:
                    if bcrypt.checkpw(password, users['password']):
                        response += str(len("<h1>Your logged in</h1>\n<p>Back to homepage <a href=\"/\">click</a> here</p>"))
                        response += p.slash_rn
                        response += "Set-Cookie: Authentication="
                        auth_cookie = SG(r"[\w]{500}").render()
                        response += auth_cookie
                        is_valid = True
                        salt = bcrypt.gensalt()
                        _hash = bcrypt.hashpw(auth_cookie.encode(), salt)
                        Statics.auth.insert_one({'Authentication': auth_cookie, "usr": username})
                    else:
                        response += str(len("<h1>Login failed</h1>\n<p>Back to homepage <a href=\"/\">click</a> here</p>"))
            response += p.slash_rn
            response += p.slash_rn
            if is_valid:
                response += "<h1>Your logged in</h1>\n<p>Back to homepage <a href=\"/\">click</a> here</p>"
            else:
                response += "<h1>Login failed</h1>\n<p>Back to homepage <a href=\"/\">click</a> here</p>"
            return response.encode()

        else:
            return_response = error(self.file_paths)

        return return_response

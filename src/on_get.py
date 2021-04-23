import string
from strgen import StringGenerator as SG
import paths
import web_sock
import Authentication
from containers import Statics


def on_get(p_obj, dictionary, socket) -> bytes:
    ret_data = ""
    visit_cookie = False
    cookie = generate_cookie()
    client_id = socket.client_address[0].replace(".", "_")
    logged_in = Authentication.check_authentication()

    if dictionary["path"] == p_obj.get_root:
        if logged_in['status']:
            return signed_in(p_obj, logged_in['name'])
        if Statics.current_cookie != "":
            visit_cookie = Authentication.check_cookie(client_id)
        print("COOOKIE: ", visit_cookie)
        ret_data = check_images(visit_cookie)
        build_str = ""
        build_str += p_obj.http_version + " " + p_obj.ok
        build_str += p_obj.slash_rn
        build_str += p_obj.content_text_html
        build_str += p_obj.slash_rn
        build_str += p_obj.content_length
        build_str += str(len(bytes(ret_data, "utf8")))
        build_str += p_obj.slash_rn
        build_str += p_obj.no_sniff
        build_str += p_obj.slash_rn
        if not visit_cookie:
            build_str += p_obj.set_cookie
            print("\n---cookie insert\n")
            print()
            print(cookie)
            print("\n---cookie insert\n")
            build_str += cookie
            Statics.db_cookies.insert_one({"client_id": client_id, "cookie": cookie})
        build_str += p_obj.slash_rn + p_obj.slash_rn
        convert_bytes = bytes(build_str, encoding='utf8')
        convert_bytes += bytes(ret_data, encoding="utf8")
        ret_data = convert_bytes

    elif dictionary["path"] == p_obj.styles_css:
        file_path = "../src/sample_page/style.css"
        ret_data = build_response(p_obj, file_path, p_obj.content_text_css, False)

    elif dictionary["path"] == p_obj.functions_js:
        file_path = "../src/sample_page/functions.js"
        ret_data = build_response(p_obj, file_path, p_obj.content_text_javascript, False)

    elif dictionary["path"] == p_obj.utf_8:
        file_path = "../src/sample_page/utf.txt"
        ret_data = build_response(p_obj, file_path, p_obj.content_text_plain, False)

    elif dictionary["path"].split("/")[1] == "image":
        file_path = "../src/sample_page"
        file_path += dictionary["path"]
        ret_data = build_response(p_obj, file_path, p_obj.content_image_jpg, False)

    elif dictionary["path"] == p_obj.signup:
        file_path = "../src/sample_page/signup.html"
        ret_data = build_response(p_obj, file_path, p_obj.content_text_html, False)

    elif dictionary["path"] == p_obj.socket:
        ret_data = web_sock.upgrade_connection(dictionary['Sec-WebSocket-Key'])
        socket.request.sendall(ret_data)
        print("client address: ", client_id + "\n")
        Statics.server_clients.append(client_id)
        Statics.server_web_sockets.append(socket.request)
        # send all the chat history to newly connected client
        all_messages = Statics.chat.find()
        for queries in all_messages:
            # print(queries['message'])
            socket.request.sendall(queries['message'])
        # now we have to keep the socket connection open
        web_sock.read_socket(socket)
    else:
        content = process_query(p_obj, dictionary["path"])
        ret_data = build_response(p_obj, content, p_obj.content_text_html, True)
    return ret_data


def check_images(is_cookie):
    home_page = "../src/sample_page/index.html"
    template_image = "<img src=\"/image/{REPLACE}\" style=\"width:300px;height:300px;\">"
    template_caption = "<p>{REPLACE}</p><br>"
    # print(template_image)
    # landing = h.read
    image_comment_block = ""
    for images in Statics.captions_images:
        image_comment_block += template_image.replace("{REPLACE}", images[1])
        image_comment_block += "\n"
        image_comment_block += template_caption.replace("{REPLACE}", images[0])
        image_comment_block += "\n"

    h = open(home_page, "r")
    new_home_page = ""
    inc = 0
    for lines in h:
        if is_cookie:
            #print(lines)
            if lines == "<h1>Welcome to this website!!</h1>\n":
                new_home_page += "<h1>Welcome back because you have a session cookie set!!!!!!</h1>\n"
            else:
                new_home_page += lines
        else:
            new_home_page += lines
        if lines == "</form>\n":
            inc += 1
        if inc == 2:
            new_home_page += image_comment_block
            inc += 1
    h.close()
    return new_home_page


def build_response(p_obj, file_path, content_type, _query) -> bytes:
    build_str = ""
    build_str += p_obj.http_version + " " + p_obj.ok
    build_str += p_obj.slash_rn
    build_str += p_obj.content_length
    read_file = ""
    if not _query:
        f = open(file_path, 'rb')
        read_file = f.read()
        length = len(read_file)
        f.close()
    else:
        read_file = bytes(file_path, encoding='utf8')
        length = len(read_file)

    # print(length)
    build_str += str(length)
    build_str += p_obj.slash_rn
    build_str += content_type
    build_str += p_obj.slash_rn
    build_str += p_obj.no_sniff
    build_str += p_obj.slash_rn + p_obj.slash_rn
    convert_bytes = bytes(build_str, encoding='utf8')
    convert_bytes += read_file
    return convert_bytes


def process_query(path_obj, path):
    files_list = []
    new_html = ""
    header = path.split("?")
    if header[0] == "/images":
        file = "image/"
        split_query = header[1].split("&")
        name_query = split_query[1].split(" ")
        name_query = name_query[0].split("=")
        images_query = split_query[0]
        images_query = images_query.split("=")
        images_query = images_query[1].split("+")
        for img in images_query:
            files_list.append(file + img + ".jpg")
        read_file = open("../src/sample_page/image_template.html",
                         "r")
        read_file = read_file.read()
        for x in range(len(files_list)):
            # print(files_list[x])
            read_file = read_file.replace("{{img}}", files_list[x], 1)
        read_file = read_file.replace("{{discription}}", "Hello " + name_query[1] + " here are the requested images")
        # print(read_file)
        return read_file
    else:
        return "Will implement 404 later"


def signed_in(p, name):
    build_str = ""
    build_str += p.http_version + " " + p.ok
    build_str += p.slash_rn
    build_str += p.content_length
    f = open("../src/sample_page/signed_in.html", 'r')
    read_file = ""
    for lines in f:
        if lines == '<h1>$$replaceMe$$</h1>\n':
            print("LINE: ", lines)
            read_file += '<h1>you are logged in as ' + name + ' </h1>'
        else:
            read_file += lines

    length = len(read_file)
    f.close()
    build_str += str(length)
    build_str += p.slash_rn
    build_str += p.content_text_html
    build_str += p.slash_rn
    build_str += p.no_sniff
    build_str += p.slash_rn + p.slash_rn
    convert_bytes = bytes(build_str, encoding='utf8')
    convert_bytes += read_file.encode()
    return convert_bytes


def generate_cookie():
    return SG(r"[\w]{30}").render()  # returns random string


class Get:
    file_paths = paths.Paths()

    def process(self, request: dict, socket):
        bytes_of_data = on_get(self.file_paths, request, socket)
        return bytes_of_data

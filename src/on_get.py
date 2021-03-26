import paths
from containers import Statics


def on_get(p_obj, dictionary) -> bytes:
    ret_data = ""
    if dictionary["path"] == p_obj.get_root:
        ret_data = check_images()
        build_str = ""
        build_str += p_obj.http_version + " " + p_obj.ok
        build_str += p_obj.slash_rn
        build_str += p_obj.content_length
        build_str += str(len(bytes(ret_data, "utf8")))
        build_str += p_obj.slash_rn
        build_str += p_obj.content_text_html
        build_str += p_obj.slash_rn
        build_str += p_obj.no_sniff
        build_str += p_obj.slash_rn + p_obj.slash_rn
        convert_bytes = bytes(build_str, encoding='utf8')
        convert_bytes += bytes(ret_data, encoding="utf8")
        ret_data = convert_bytes

    elif dictionary["path"] == p_obj.styles_css:
        file_path = "src/sample_page/style.css"
        ret_data = build_response(p_obj, file_path, p_obj.content_text_css, False)

    elif dictionary["path"] == p_obj.functions_js:
        file_path = "src/sample_page/functions.js"
        ret_data = build_response(p_obj, file_path, p_obj.content_text_javascript, False)

    elif dictionary["path"] == p_obj.utf_8:
        file_path = "src/sample_page/utf.txt"
        ret_data = build_response(p_obj, file_path, p_obj.content_text_plain, False)

    elif dictionary["path"].split("/")[1] == "image":
        file_path = "src/sample_page"
        file_path += dictionary["path"]
        ret_data = build_response(p_obj, file_path, p_obj.content_image_jpg, False)
    else:
        content = process_query(p_obj, dictionary["path"])
        ret_data = build_response(p_obj, content, p_obj.content_text_html, True)
    return ret_data


def check_images():
    home_page = "src/sample_page/index.html"
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
        read_file = open("src/sample_page/image_template.html",
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


class Get:
    file_paths = paths.Paths()

    def process(self, request: dict):
        bytes_of_data = on_get(self.file_paths, request)
        return bytes_of_data

import bcrypt

from containers import Statics
from paths import Paths


def check_cookie(client):
    # {"client_id": client, "cookie": Statics.current_cookie}
    search = Statics.db_cookies.find()
    print("IP: ", client)
    for x in search:
        print(x)
        if x["client_id"] == client and x["cookie"] == Statics.current_cookie:
            print("Has the correct cookie: GOOD")
            return True
    return False


def check_authentication():
    current_token = Statics.token
    salt = bcrypt.gensalt()
    _hash = bcrypt.hashpw(current_token.encode(), salt)
    print("Current token: ", current_token)
    get_token = Statics.auth.find({"Authentication": current_token})
    user_name = "----"
    login = False
    for x in get_token:
        user_name = x['usr']
    if user_name != "----":
        login = True
    return {'status': login, 'name': user_name}


def check_password(psw):
    p_length = False
    p_lower = False
    p_upper = False
    p_number = False
    p_special = False
    p_exclamation = False

    if len(psw) < 8:
        return False
    else:
        p_length = True

    for character in psw:
        asc = ord(character)
        if character == "!":
            p_exclamation = True
        elif 65 <= asc <= 90:
            p_upper = True
        elif 32 <= asc <= 47 or 58 <= asc <= 64 or 91 <= asc <= 96 or 123 <= asc <= 126:
            p_special = True
        elif 48 <= asc < 57:
            p_number = True
        elif 97 <= asc <= 122:
            p_lower = True

    check_all = [p_length, p_lower, p_upper, p_number, p_special, p_exclamation]

    for check in check_all:
        if not check:
            return False

    return True


def invalid_password():
    p_obj = Paths()
    build_str = ""
    build_str += p_obj.http_version + " " + p_obj.ok
    build_str += p_obj.slash_rn
    build_str += p_obj.content_length
    f = open("../src/sample_page/signup_error.html", "rb")
    read = f.read()
    build_str += str(len(read))
    build_str += p_obj.slash_rn
    build_str += p_obj.content_text_html
    build_str += p_obj.slash_rn
    build_str += p_obj.no_sniff
    build_str += p_obj.slash_rn + p_obj.slash_rn
    build_str = build_str.encode()
    build_str += read
    return build_str

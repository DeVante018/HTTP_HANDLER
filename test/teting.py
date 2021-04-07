import unittest
import hashlib
import base64


def upgrade_connection(given):
    # code snippet from my implementation
    pre = given + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    my_hash = hashlib.sha1(pre.encode()).hexdigest()  # Hex so I can encode to base64
    result = base64.b64encode(bytes.fromhex(my_hash)).decode()
    return result


class TestSha1Hash(unittest.TestCase):
    def test_1(self):
        self.assertEqual(upgrade_connection("105Y8GZdbUzIP2ghlKHxVA=="), "85eihQGDJmKcMgDbxaudS79vOGs=")

    def test_2(self):
        self.assertEqual(upgrade_connection("1ZIgzXtmuAP6WZEF6YkG9A=="), "C6JA/Arck8WNqh2DYfEbn+MJkHA=")

    def test_3(self):
        self.assertEqual(upgrade_connection("rWQnD/pRf0iu7d9vKkHN6Q=="), "KaYD88U7lEbpvlN67Ma8wBat30s=")
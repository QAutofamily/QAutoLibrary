from hashlib import sha256
import base64
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:

    def __init__( self, key ):
        self.BS = 16
        self.key = bytes(key, 'utf-8')
        self.pad = lambda s: bytes(s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS), 'utf-8')
        self.unpad = lambda s : s[0:-ord(s[-1:])]

    def encrypt( self, raw ):
        raw = self.pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new(self.key, AES.MODE_CFB, iv )
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:self.BS]
        cipher = AES.new(self.key, AES.MODE_CFB, iv )
        return self.unpad(cipher.decrypt( enc[self.BS:] )).decode('utf8')
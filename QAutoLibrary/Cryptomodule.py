"""
#    QAutomate Ltd 2020. All rights reserved.
#
#    Copyright and all other rights including without limitation all intellectual property rights and title in or
#    pertaining to this material, all information contained herein, related documentation and their modifications and
#    new versions and other amendments (QAutomate Material) vest in QAutomate Ltd or its licensor's.
#    Any reproduction, transfer, distribution or storage or any other use or disclosure of QAutomate Material or part
#    thereof without the express prior written consent of QAutomate Ltd is strictly prohibited.
#
#    Distributed with QAutomate license.
#    All rights reserved, see LICENSE for details.
"""

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
import struct
import hashlib
import math
import os
import base64
from Crypto.Cipher import AES

IV_SIZE = 16    # 128 bit, fixed for the AES algorithm
KEY_SIZE = 32   # 256 bit meaning AES-256, can also be 128 or 192 bits
SALT_SIZE = 16  # This size is arbitrary


BS = 32
pad = lambda s: s + (((16 - len(s)) % 16) * chr(16))

cleartext = "ABBAABBAABBAABBA"
password = "AABB"
salt = os.urandom(SALT_SIZE)

iv= hashlib.sha256(salt).digest()[0:IV_SIZE]
key= hashlib.sha256(salt+password).digest()



encrypted = salt+AES.new(key, AES.MODE_CBC, iv).encrypt(pad(cleartext.encode("utf8")))
for b in encrypted:
    print(hex(ord(b)))


encryptedB =  base64.b64encode(encrypted)
print encryptedB


#---------------------------------------------------------------------

encrypted_dec = base64.b64decode(encryptedB)
salt = encrypted_dec[0:SALT_SIZE]
iv= hashlib.sha256(salt).digest()[0:IV_SIZE]
key= hashlib.sha256(salt+password).digest()


cleartext = AES.new(key, AES.MODE_CBC, iv).decrypt(encrypted_dec[SALT_SIZE:])
print cleartext
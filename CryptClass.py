import hashlib
import math
import os
import base64
from Crypto.Cipher import AES


class CryptClass(object):
    IV_SIZE = 16    # 128 bit, fixed for the AES algorithm
    KEY_SIZE = 32   # 256 bit meaning AES-256, can also be 128 or 192 bits
    SALT_SIZE = 16  # This size is arbitrary
    __password  = 0


    def __init__(self):
	#password get from config
	self.__password = "AABB"

    def __pad(self, text):
	return text + (((16 - len(text)) % 16) * chr(16 - len(text) % 16))

    def Encode(self, data):
	salt = os.urandom(CryptClass.SALT_SIZE)
	iv= hashlib.sha256(salt).digest()[0:CryptClass.IV_SIZE]
	key= hashlib.sha256(salt+self.__password).digest()
	encrypted = salt+AES.new(key, AES.MODE_CBC, iv).encrypt(self.__pad(data.encode("utf8")))

	#for b in encrypted:
	#    print(hex(ord(b)))

	result = base64.b64encode(encrypted)
	#print "ENCODE = " + data +"\n" + result
	return result

    def Decode(self, data):
	encrypted = base64.b64decode(data)
	salt = encrypted[0:CryptClass.SALT_SIZE]
	iv= hashlib.sha256(salt).digest()[0:CryptClass.IV_SIZE]
	key= hashlib.sha256(salt+self.__password).digest()

	#for b in iv:
	#    print(hex(ord(b)))

	clearText = AES.new(key, AES.MODE_CBC, iv).decrypt(encrypted[CryptClass.SALT_SIZE:])
	#print "DECOD = " +clearText +"\n" + data
	
	return clearText

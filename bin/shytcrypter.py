from Crypto.Cipher import AES
import os
import sys
import base64
import hashlib
import getpass
# A shyt crypter for shyt crypto functions

BLOCK_LENGTH = 32
IV_BLOCK_LENGTH = 16
PADDING = '~'
AES_MODE = AES.MODE_CBC


def get_password():
    string_password = getpass.unix_getpass(prompt="Secret: ", stream=sys.stderr)
    string_hash = password_to_hash(string_password)
    return string_hash


def password_to_hash(string_password):
    string_hash = hashlib.sha256(string_password.encode()).digest()
    return string_hash


def pad(s):
    return s + (BLOCK_LENGTH - len(s) % BLOCK_LENGTH) * PADDING


def encode_AES(c, s):
    return base64.b64encode(c.encrypt(pad(s)))


def decode_AES(c, e):
    return c.decrypt(base64.b64decode(e)).decode('UTF-8').rstrip(PADDING)


def shyt_crypt(private_info):
    #pad = lambda s: s + (BLOCK_LENGTH - len(s) % BLOCK_LENGTH) * PADDING
    #encode_AES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    # secret = get_password()

    secret = os.urandom(BLOCK_LENGTH)
    iv = os.urandom(IV_BLOCK_LENGTH)
    cipher = AES.new(secret, AES_MODE, iv)
    encrypted_info = encode_AES(cipher, private_info)
    return encrypted_info, iv, secret


def shyt_decrypt(encrypted_info, iv, secret):
    #decode_AES = lambda c, e: c.decrypt(base64.b64decode(e)).decode('UTF-8').rstrip(PADDING)
    cipher = AES.new(secret, AES_MODE, iv)
    private_info = decode_AES(cipher, encrypted_info)
    return private_info

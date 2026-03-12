from base64 import b64decode
from Crypto.Cipher import AES

# Which keylength AES is set to can be seen by looking at the amount of characters in the key used to encrypt a file. 
# 16 bytes → AES-128
# 24 bytes → AES-192
# 32 bytes → AES-256
# Despite the fact that each ASCII character is 7 bits long they are almost always stored in 8 bits, which means that-
# Each character represents 1 byte. SECRETSAREHIDDEN has 16 characters, therefore 16 bytes which means AES-128
key = b"SECRETSAREHIDDEN"   

def ECB_decrypt(ciphertext, key):
    """Accepts a ciphertext in byte-form,
    as well as 16-byte key, and returns 
    the corresponding plaintext.

    Parameters
    ----------
    ciphertext : bytes
        ciphertext to be decrypted
    key : bytes
        key to be used in decryption

    Returns
    -------
    bytes
        decrypted plaintext
    """

    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    
    return plaintext


# Laat deze asserts onaangetast & onderaan je code!
ciphertext = b64decode('86ueC+xlCMwpjrosuZ+pKCPWXgOeNJqL0VI3qB59SSY=')
key = b'SECRETSAREHIDDEN'
assert ECB_decrypt(ciphertext, key)[:28] == \
    b64decode('SGFzdCBkdSBldHdhcyBaZWl0IGZ1ciBtaWNoPw==')
from base64 import b64decode
from Crypto.Cipher import AES
from secrets import token_bytes

def pkcs7_pad(plaintext, blocksize):
    """Appends the plaintext with n bytes,
    making it an even multiple of blocksize.
    Byte used for appending is byteform of n.

    Parameters
    ----------
    plaintext : bytes
        plaintext to be appended
    blocksize : int
        blocksize to conform to

    Returns
    -------
    plaintext : bytes
        plaintext appended with n bytes
    """

    # Determine how many bytes to append
    n = blocksize - len(plaintext)%blocksize
    # Append n*(byteform of n) to plaintext
    # n is in a list as bytes() expects iterable
    plaintext += (n*bytes([n]))
    return plaintext

def ECB_oracle(plaintext, key):
    """Appends a top-secret identifier to the plaintext
    and encrypts it under AES-ECB using the provided key.

    Parameters
    ----------
    plaintext : bytes
        plaintext to be encrypted
    key : bytes
        16-byte key to be used in decryption

    Returns
    -------
    ciphertext : bytes
        encrypted plaintext
    """
    plaintext += b64decode('U2F5IG5hIG5hIG5hCk9uIGEgZGFyayBkZXNlcnRlZCB3YXksIHNheSBuYSBuYSBuYQpUaGVyZSdzIGEgbGlnaHQgZm9yIHlvdSB0aGF0IHdhaXRzLCBpdCdzIG5hIG5hIG5hClNheSBuYSBuYSBuYSwgc2F5IG5hIG5hIG5hCllvdSdyZSBub3QgYWxvbmUsIHNvIHN0YW5kIHVwLCBuYSBuYSBuYQpCZSBhIGhlcm8sIGJlIHRoZSByYWluYm93LCBhbmQgc2luZyBuYSBuYSBuYQpTYXkgbmEgbmEgbmE=')
    plaintext = pkcs7_pad(plaintext, len(key))
    cipher = cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext

# Genereer een willekeurige key
key = token_bytes(16)

#####################################
###  schrijf hieronder jouw code  ###
### verander code hierboven niet! ###
#####################################
  
def find_block_length():
    """Finds the block length used by the ECB oracle.

    Returns
    -------
    blocksize : integer
        blocksize used by ECB oracle
    """
    base_len = len(ECB_oracle(b"", key))

    i = 1
    blocksize = 0

    while True:
        #The part that monitors the length of the encrypted data. 
        new_len = len(ECB_oracle(b"A" * i, key))
        #If the new_len > base_len then that means that the added amount of data necessitated the creation of a new block.
        #The difference is expressed in bytes and is your blocksize. 
        if new_len > base_len:

            blocksize = new_len - base_len
            break

        i += 1
    return blocksize

# variables
block = find_block_length()
secret_len = len(ECB_oracle(b"", key))
match = b""

# by calling ECB_oracle with empty plaintext it will return the encrypted seret + padding. 
for i in range(secret_len):
    # note to future self, prefix always needs to be 1 shorter than len(block) and (i%block) resets the index counter.
    # initially used "a" but during one of the instances where i let chatgpt check my code it suggested using "A" 
    # and cited convention as a reason.
    prefix = b"A" * (block - 1 - (i % block)) 
    # floor division of i by len(block) followed by a multiplication len(block) sets the start value to be used.
    # The stop value however is incorporated in the target variable as start+block, essentially the start value plus the len(block) 
    # target is specified via index slicing, avoiding having to load and store redundant information. 
    start = (i // block) * block
    target = ECB_oracle(prefix, key)[start:start+block]
    # Despite there being only 128 ASCII characters, Chatgpt suggested I set this value to 256 just in case. 
    # Since doing so comes at little consequence due to the inclusion of a break condition if the secret message character ends 
    # up matching I decided doing so would be nice to have at no expense. 
    for j in range(256):
        if ECB_oracle(prefix + match + bytes([j]), key)[start:start+block] == target:
            match += bytes([j])
            break

print(match[:-1].decode())
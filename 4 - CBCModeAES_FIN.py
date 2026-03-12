from base64 import b64decode
from Crypto.Cipher import AES
import Crypto.Cipher

def fixed_length_xor(text, key):
    """
    Performs a binary XOR of two equal-length strings. 
    
    Parameters
    ----------
    text : bytes
        bytes-object to be xor'd w/ key
    key : bytes
        bytes-object to be xor'd w/ text
        
    Returns
    -------
    bytes
        binary XOR of text & key
    """
    # There are multiple ways to do this, I chose this one because it is a clean one liner-
    # requiring no additional imports. zip creates a list of tuples from arguments text and-
    # key, iterates over each tuple via list comprehension and performs a binary XOR on-
    # each element as it does so.

    xor_output = bytes([a ^ b for a, b in zip(text, key)])

    return xor_output

def repeating_key_xor(text, key):
    """Takes two bytestrings and XORs them, returning a bytestring.
    Extends the key to match the text length.
    
    Parameters
    ----------
    text : bytes
        bytes-object to be xor'd w/ key
    key : bytes
        bytes-object to be xor'd w/ text
        
    Returns
    -------
    bytes
        binary XOR of text & key
    """

    # Step 1: First we find out how many times we will need to repeat the key until its padded-
    # length accommodates the text length. To do so we will divide the text length by the key-
    # length. However, since there is no guarantee this will result in a round number, and -
    # in order to make sure that the padding accommodates the full text length, we will need-
    # to perform a ceiling division. We accomplish that using the formula (a+b-1)//b
    ltext = len(text)
    lkey = len(key)
    ceildiv = (ltext + lkey - 1) // lkey

    # Step 2: We then multiply the key by the product of our ceiling divison and cut the-
    # excess lenght from the padded key using index slicing. 
    pad_key = (key * ceildiv)[:len(text)] 
    
    # Step 3: We feed the resulting padded key into the fixed_length_xor(text,key) function-
    # Store the outcome in variable xor_output which is then returned by this function.  
    xor_output = fixed_length_xor(text,pad_key)

    return xor_output

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

    cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    
    return plaintext

def CBC_decrypt(ciphertext, key, IV):
    """Decrypts a given plaintext in CBC mode.
    First splits the ciphertext into keylength-size blocks,
    then decrypts them individually w/ ECB-mode AES
    and XOR's each result with either the IV
    or the previous ciphertext block.
    Appends decrypted blocks together for the output.

    Parameters
    ----------
    ciphertext : bytes
        ciphertext to be decrypted
    key : bytes
        Key to be used in decryption
    IV : bytes
        IV to be used for XOR in first block

    Returns
    -------
    bytes
        Decrypted plaintext
        """
    
    
    block_size = 16
    plaintext = b""
    prev_block = IV

    for i in range(0, len(ciphertext), block_size):
        block = ciphertext[i:i+block_size]
        decrypted = ECB_decrypt(block, key)
        plaintext_block = fixed_length_xor(decrypted, prev_block)
        plaintext += plaintext_block
        prev_block = block
        
    return(plaintext)


# Laat dit blok code onaangetast & onderaan je code!
a_ciphertext = b64decode('e8Fa/QnddxdVd4dsL7pHbnuZvRa4OwkGXKUvLPoc8ew=')
a_key = b'SECRETSAREHIDDEN'
a_IV = b'WE KNOW THE GAME'
assert CBC_decrypt(a_ciphertext, a_key, a_IV)[:18] == b64decode('eW91IGtub3cgdGhlIHJ1bGVz')
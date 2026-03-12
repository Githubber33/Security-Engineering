from base64 import b64encode

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
    xor_output = bytes([a ^ b for a, b in zip(text, key)])

    return xor_output

# Laat deze asserts onaangetast!
assert type(fixed_length_xor(b'foo',b'bar')) == bytes
assert b64encode(fixed_length_xor(b'foo',b'bar')) == b'BA4d'

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

# Laat deze asserts onaangetast!
assert type(repeating_key_xor(b'all too many words',b'bar')) == bytes
assert b64encode(repeating_key_xor(b'all too many words',b'bar'))\
    == b'Aw0eQhUdDUEfAw8LQhYdEAUB'

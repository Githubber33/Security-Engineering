# Step 1.) First we import the base64 module
import base64


def string_to_b64(asciiString):
    """
    Converts a given ASCII-string to its b64-encoded equivalent.

    Parameters
    ----------
    asciiString : string
        string to be converted

    Returns
    -------
    bytes
        b64-encoded bytes-object representing the original string
    """

    # Step 2 The link in the assignment to GeeksforGeeks provides an overvieuw of a block of- 
    # code that both encodes and decodes. Since we only need to encode here, we removed the- 
    # decoding parts and adjusted the arguments/variables to correspond with those used in- 
    # this function.

    sample_string_bytes = asciiString.encode("ascii")
    b64String = base64.b64encode(sample_string_bytes)

    return b64String

# Laat deze asserts onaangetast!
assert type(string_to_b64("foo")) == bytes
assert string_to_b64("Hello World") == b'SGVsbG8gV29ybGQ='

def b64_to_string(b64String):
    """
    Converts a given b64-string to its ASCII equivalent.

    Parameters
    ----------
    b64String : bytes
        b64-encoded bytesobject to be converted

    Returns
    -------
    string
        ASCII string
    """

    #Step 3 Similar to what we did at step 2. removed the encoding parts and adjusted the-
    # variables/arguments of the code on GeeksforGeeks to correspond with those used by this-
    # function.

    sample_string_bytes = base64.b64decode(b64String)
    asciiString = sample_string_bytes.decode("ascii")

    return asciiString

# A few lines of code used for checking the outcome.
#print(type(b64_to_string("SGVsbG8gV29ybGQ=")))
#print(b64_to_string("SGVsbG8gV29ybGQ="))


# Laat deze asserts onaangetast!
assert type(b64_to_string("SGVsbG8gV29ybGQ=")) == str
assert b64_to_string("SGVsbG8gV29ybGQ=") == "Hello World"


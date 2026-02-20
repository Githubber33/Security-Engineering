import socket
import ipaddress
from scapy.all import ARP, Ether, srp

def get_user_input(): # Asks the user to select which type of scan the program needs to do, target(s) and ports.
    print("Select type of scan: \n 1. Subnet (e.g. 192.168.1.0/24), \n 2. Range (e.g. 192.168.178.1-49), \n 3. Single (e.g. 192.168.178.5)")

    choice = input("Enter your choice (1-3): ") 

    if choice == "1": # if statement to safe the choice of the user.
        scan_type = "Subnet"
    elif choice == "2":
        scan_type = "Range"
    elif choice == "3":
        scan_type = "Single"
    else:
        print("Invalid choice")
        return None

    print(f"You selected: {scan_type}")
    
    target_input = input("Enter target IP / range / subnet (only accepts previous selected type): ") # asks the user to put in there target(s). This gets saved into target_input.
    ports_input = input("Enter ports (e.g. 80,443 or 1-1000): ") # asks the user for the ports to scan.
    print("\n====== Summary ======") # shows a quick summary of what the user has put in.
    print("Scan type:", scan_type)
    print("Targets:", target_input)
    print("Scan for ports:", ports_input)
    print("=====================")
    return scan_type, target_input, ports_input # retuns the scan_type, target(s) and port(s).
    
   
def target_list(scan_type, target_input):
    """
    Generate a list of target IP addresses based on the selected scan type.
    This function supports three types of input:

    1. Subnet:
        Example: "192.168.1.0/24"
        - Uses the ipaddress library to generate all usable host IPs
        - Excludes network and broadcast addresses

    2. Range:
        Example: "192.168.1.10-20"
        - Uses the first three octets as the base network
        - Generates IPs from the start value to the end value of the last octet

    3. Single:
        Example: "192.168.1.5"
        - Returns a list containing only one IP address

    Parameters:
        scan_type (str): Type of scan ("Subnet", "Range", or "Single")
        target_input (str): Input string representing the target(s)

    Returns:
        list[str]: A list of IP addresses as strings

    Raises:
        ValueError: If the input format is invalid
    """
    if scan_type == "Subnet": 
        network = ipaddress.ip_network(target_input, strict=False) # creates individual ipadresses as objects with the ipaddress libary
        return [str(ip) for ip in network.hosts()] # with a list comprehension it stores the individual ip addresses in the list as a string
    
    elif scan_type == "Range":
        start_ip, end_octet = target_input.split("-") # this splits the first 3 octets with the last 
        start_octet = int(start_ip.split(".")[-1])

        base = ".".join(str(start_ip).split(".")[:3])
        return [f"{base}.{i}" for i in range(start_octet, int(end_octet) + 1)]
    elif scan_type == "Single":
        ip = ipaddress.ip_address(target_input)
        return [str(ip)]


def ports(ports_input): # Melano
    print()
    
def discover_host(targets):
    arp = ARP(pdst=targets)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ether / arp
    arp_result = srp(packet, timeout=2, verbose=0)[0]

    discoverd_ip_mac = []

    for sent, recieved in arp_result:
        ip = recieved.psrc
        mac = recieved.hwsrc

        discoverd_ip_mac.append({
            "ip": ip,
            "mac": mac
        })

    return discoverd_ip_mac

def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None

def scan_host(discoverd_ip_mac, port_list):
    scanned_hosts = []
    for host in discoverd_ip_mac:
        ip = host["ip"]
        mac = host["mac"]
        hostname = resolve_hostname(ip) or "Not availible"

    return


    



scan_type, target_input, ports_input = get_user_input()

confirm = input("\nPress ENTER to continue or type 'q' to quit: ")
if confirm.lower() == "q":
    print("Scan cancelled.")
    exit()

targets = target_list(scan_type, target_input)


discovered_ip_mac = discover_host(targets)
print("\nDiscovered hosts:")
for d in discovered_ip_mac:
    print(f"[+] {d['ip']}  {d['mac']}")




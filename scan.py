import socket
import ipaddress
from scapy.all import ARP, Ether, srp, conf
import nmap
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor, as_completed


conf.use_pcap = True
conf.sniff_promisc = True
conf.checkIPaddr = False

def get_user_input(): # Asks the user to select which type of scan the program needs to do, target(s) and ports.
    """
    Asks the user which type of scan the user wants to preform.
    There are 3 types: a whole subnet, a range of hosts and a single IP.
    This function also asks which subnet, range or single IP the program needs to scan.
    After the input it shows a summary of what the user has put in the program. 

    """
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


def ports(ports_input):
    """
    Convert port input string to a list of integers.

    Supports:
    - Single ports: "80"
    - Multiple: "80,443"
    - Range: "1-1000"
    """

    ports = set()

    for part in ports_input.replace(" ", "").split(","):
        if "-" in part:
            start, end = part.split("-")
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(part))

    return sorted(ports)
    
    
def discover_host(targets):
    """
    Using Scapy and ARP requests this function discovers the hosts in the local network.
    You can specify which interface you want to use by GUID. by running the following command in powershell you can get the GUID of the interface: 
    
    Get-NetAdapter | Select Name, InterfaceGuid 

    The function gets a list of targets and checks if any of those targets respond to a ARP request.
    If they do respond to the request, the function saves the IP and MAC address to a list.
    if everything is finished then the list of all the discoverd IP and MAC adresses gets returned. 
    
    """
    # conf.iface = r"\Device\NPF_{5E41DDD6-DC7A-4940-9D5F-A907912736C5}" # Specify the interface in the brackets {} using its GUID
    arp = ARP(pdst=targets)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    # print("Using iface:", conf.iface) # debug line to see what interface the program is using by GUID
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
    """
    This resolve_hostname() function 
    """
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None

def os_detection(target):
    """
    os_detection(target) is being used to detect the os. this function uses the nmap library with the -O argument.
    The target is the IP adress of the host that nmap wil scan for the OS and try to make a guess.
    When nmap will take a guess, the best match/guess will return. If there coulnt make a guess the function will return the error.

    """
    nm = nmap.PortScanner()
    try:
        nm.scan(target, arguments="-O --osscan-guess")
        if target not in nm.all_hosts():
            return "Unknown"

        osmatches = nm[target].get("osmatch", [])
        if not osmatches:
            return "Unknown"

        best = osmatches[0]
        name = best.get("name", "Unknown")
        acc = best.get("accuracy", "?")
        return f"{name} ({acc}% match)"
    except Exception as e:
        return f"Unknown (OS scan failed: {e})"
        
def service_detection(ip, scanned_ports):
    """
    service_detection(ip, scanned_ports) wil detect the service based on the IP adress and port number.
    Nmap wil scan the host with the associated port with the -sV argument.
    """
    nm = nmap.PortScanner()
    services = {}
    if not scanned_ports:
        return services

    try:
        ports_arg = ",".join(str(p) for p in scanned_ports)
        nm.scan(ip, ports=ports_arg, arguments="-sV --version-light")

        tcp_info = nm[ip].get("tcp", {}) if ip in nm.all_hosts() else {}

        for p in scanned_ports:
            entry = tcp_info.get(p, {})
            name = entry.get("name", "unknown")
            product = entry.get("product", "")
            version = entry.get("version", "")
            extrainfo = entry.get("extrainfo", "")

            details = " ".join(x for x in [product, version, extrainfo] if x).strip()
            services[p] = f"{name}" + (f" ({details})" if details else "")
        return services

    except Exception as e:
        for p in scanned_ports:
            services[p] = f"unknown (service scan failed: {e})"
        return services

def check_port(ip, port, timeout=0.2):
    """
    The check_port(ip, port, timeout=0.2) function will check if the port is open.
    It will achieve this by connecting with a socket. it will try to connect to it for 0.2s otherwise the port is closed.
    
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        return port if sock.connect_ex((ip, port)) == 0 else None
    finally:
        sock.close()

def scan_open_ports(ip, port_list, workers=200, timeout=0.2):
    open_ports = []
    workers = min(workers, len(port_list)) if port_list else 0
    if workers == 0:
        return open_ports

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(check_port, ip, p, timeout) for p in port_list]
        for f in as_completed(futures):
            p = f.result()
            if p is not None:
                open_ports.append(p)

    return sorted(open_ports)

def scan_one_host(host, port_list):
    ip = host["ip"]
    mac = host["mac"]
    hostname = resolve_hostname(ip) or "Not available"

    open_ports = scan_open_ports(ip, port_list, workers=200, timeout=0.2)

    services = service_detection(ip, open_ports) if open_ports else {}

   
    os_name = os_detection(ip)

    return {
        "ip": ip,
        "mac": mac,
        "hostname": hostname,
        "os": os_name,
        "ports": [
            {"port": p, "protocol": "TCP", "service": services.get(p, "unknown")}
            for p in open_ports
        ]
    }

    

def scan_host(discoverd_ip_mac, port_list, host_workers=5):
    scanned_hosts = []
    with ThreadPoolExecutor(max_workers=host_workers) as ex:
        futures = [ex.submit(scan_one_host, host, port_list) for host in discoverd_ip_mac]
        for future in as_completed(futures):
            scanned_hosts.append(future.result())
    return scanned_hosts

def main():
    scan_type, target_input, ports_input = get_user_input()
    confirm = input("\nPress ENTER to continue or type 'q' to quit: ")
    if confirm.lower() == "q":
        print("Scan cancelled.")
        exit()


    targets = target_list(scan_type, target_input)
    port_list = ports(ports_input)


    discovered_ip_mac = discover_host(targets)
    print("\nDiscovered hosts:")
    for d in discovered_ip_mac:
        print(f"[+] {d['ip']}  {d['mac']}")


    print("\nScanning the network:")
    scanned_hosts = scan_host(discovered_ip_mac, port_list)
    table_data = []
    headers = ["IP", "MAC", "Hostname", "OS", "Port", "Service"]
    for host in scanned_hosts:
        ip = host["ip"]
        mac = host["mac"]
        hostname = host["hostname"]
        os_name = host["os"]

        first = True  # <-- belangrijk

        if not host["ports"]:
            table_data.append([ip, mac, hostname, os_name, "-", "-"])
        else:
            for p in host["ports"]:
                if first:
                    table_data.append([
                        ip,
                        mac,
                        hostname,
                        os_name,
                        p["port"],
                        p["service"]
                    ])
                    first = False
                else:
                    table_data.append([
                        "", "", "", "",   # <-- leeg laten
                        p["port"],
                        p["service"]
                    ])


    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

main()

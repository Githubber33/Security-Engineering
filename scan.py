import socket
import ipaddress

def get_user_input():
    print("Select type of scan: \n 1. Subnet (e.g. 192.168.1.0/24), \n 2. Range (e.g. 192.168.178.1-49), \n 3. Single (e.g. 192.168.178.5)")

    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        scan_type = "Subnet"
    elif choice == "2":
        scan_type = "Range"
    elif choice == "3":
        scan_type = "Single"
    else:
        print("Invalid choice")
        return None

    print(f"You selected: {scan_type}")
    
    target_input = input("Enter target IP / range / subnet (only accepts previous selected type): ")
    ports_input = input("Enter ports (e.g. 80,443 or 1-1000): ")
    print("\n====== Summary ======")
    print("Scan type:", scan_type)
    print("Target:", target_input)
    print("Ports:", ports_input)
    print("=====================")
    return scan_type, target_input, ports_input
    
   
def target_list(scan_type, target_input):
    if scan_type == "Subnet":
        network = ipaddress.ip_network(target_input, strict=False)
        return [str(ip) for ip in network.hosts()]
    
    elif scan_type == "Range":
        start_ip, end_octet = target_input.split("-")
        start_octet = int(start_ip.split(".")[-1])

        base = ".".join(str(start_ip).split(".")[:3])
        return [f"{base}.{i}" for i in range(start_octet, int(end_octet) + 1)]
    elif scan_type == "Single":
        ip = ipaddress.ip_address(target_input)
        return [str(ip)]


def ports(ports_input):
    print()
    



scan_type, target_input, ports_input = get_user_input()
targets = target_list(scan_type, target_input)
print("Targets:", targets)


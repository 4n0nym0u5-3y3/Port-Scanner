import argparse
import socket
from colorama import init, Fore
from threading import Thread, Lock
from queue import Queue

# Initialize colorama

init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX

# Default number of threads

N_THREADS = 200

# Queue for threads

q = Queue()
print_lock = Lock()

open_ports = []

def port_scan(port):
    """
    Scan a port on the global variable `host`.
    """
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect((host, port))
    except (socket.timeout, socket.error):
        if args.verbose:
            with print_lock:
                print(f"{GRAY}{host:15}:{port:5} is closed  {RESET}", end='\r')
    else:
        with print_lock:
            print(f"{GREEN}{host:15}:{port:5} is open    {RESET}")
            open_ports.append(port)
    finally:
        s.close()


def scan_thread():
    global q
    while True:
        worker = q.get()
        port_scan(worker)
        q.task_done()


def main(host, ports):
    global q
    for t in range(args.threads):
        t = Thread(target=scan_thread)
        t.daemon = True
        t.start()

    for worker in ports:
        q.put(worker)
    
    q.join()

    if open_ports:
        print(f"\n{GREEN}Open ports:{RESET}")
        for port in open_ports:
            print(f"{GREEN}{port}{RESET}")
    else:
        print(f"{GRAY}No open ports found.{RESET}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple port scanner")
    parser.add_argument("host", help="Host to scan.")
    parser.add_argument("--ports", "-p", dest="port_range", default="1-65535", help="Port range to scan, default is 1-65535 (all ports)")
    parser.add_argument("--threads", "-t", type=int, default=N_THREADS, help="Number of threads to use, default is 200")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode to see all ports (open and closed)")
    args = parser.parse_args()

    try:
        host = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"{Fore.RED}Error: Hostname could not be resolved.{RESET}")
        exit(1)

    try:
        start_port, end_port = map(int, args.port_range.split("-"))
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError
    except ValueError:
        print("Invalid port range. Please provide a valid range in the format 'start-end', where start and end are between 1 and 65535.")
        exit(1)

    ports = [p for p in range(start_port, end_port + 1)]

    main(host, ports)

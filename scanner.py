import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from threading import Thread
import socket
import requests


def get_geo_info(ip_address):
    token = "" # use your API-key
    url = f"http://ipinfo.io/{ip_address}?token={token}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "IP Address": data.get("ip"),
            "City": data.get("city"),
            "Region": data.get("region"),
            "Country": data.get("country"),
            "Location": data.get("loc"),
            "ISP": data.get("org"),
            "AS": data.get("asn"),
            "Hostname": data.get("hostname"),
        }
    else:
        return {"Error": f"Failed to retrieve information for {ip_address}"}


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner")

        self.target_label = ttk.Label(root, text="Target IP Address:")
        self.target_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.target_entry = ttk.Entry(root, width=15)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.ports_label = ttk.Label(root, text="Ports:")
        self.ports_label.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        self.ports_entry = ttk.Entry(root, width=15)
        self.ports_entry.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.scan_button = ttk.Button(root, text="Scan", command=self.start_scan)
        self.scan_button.grid(row=0, column=5, padx=5, pady=5)

        self.result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
        self.result_text.grid(row=1, column=0, columnspan=6, padx=5, pady=5)

    def start_scan(self):
        target = self.target_entry.get()
        ports_entry = self.ports_entry.get()

        ports = parse_ports(ports_entry)

        self.result_text.delete(1.0, tk.END)

        def scan():
            if ports is None:
                ports_scan = range(1, 2**16)
            else:
                ports_scan = ports

            open_ports = Open_ports(target, ports_scan)
            services = scan_services(target, open_ports)
            host_info = get_host_info(target)
            geo_info = get_geo_info(target)

            results = {
                "Host Information": host_info,
                "Geographical Information": geo_info,
                "Open Ports": open_ports,
                "Services": services
            }

            self.display_results(results)

        thread = Thread(target=scan)
        thread.start()

    def display_results(self, results):
        for category, info in results.items():
            self.result_text.insert(tk.END, f"{category}:\n")
            if isinstance(info, dict):
                for key, value in info.items():
                    self.result_text.insert(tk.END, f"  {key}: {value}\n")
            elif isinstance(info, list):
                for item in info:
                    self.result_text.insert(tk.END, f"  - {item}\n")
            else:
                self.result_text.insert(tk.END, f"  {info}\n")
            self.result_text.insert(tk.END, "\n")


def parse_ports(ports_entry):
    if not ports_entry:
        return None
    ports = []
    for part in ports_entry.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part.strip()))
    return ports


def Open_ports(target, ports):
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        if result == 0:
            open_ports.append(port)
    return open_ports


def scan_services(target, open_ports):
    services = []
    for port in open_ports:
        try:
            service = socket.getservbyport(port)
            services.append((port, service))
        except socket.error:
            services.append((port, "Unknown"))
    return services


def get_host_info(target):
    try:
        host_info = socket.gethostbyaddr(target)
        return {
            "IP Address": target,
            "Hostname": host_info[0],
            "Aliases": host_info[1],
            "Canonical Name": host_info[2]
        }
    except socket.herror:
        return {"IP Address": target, "Hostname": "Unknown"}


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

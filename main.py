import netifaces as ni
import os
import platform
import subprocess
import socket
import urllib.request
import time
from datetime import timedelta
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_interface_info():
    interfaces = ni.interfaces()
    data = []

    for iface in interfaces:
        try:
            if ni.AF_INET in ni.ifaddresses(iface):
                ip_info = ni.ifaddresses(iface)[ni.AF_INET][0]
                ip = ip_info.get('addr', '-')
                netmask = ip_info.get('netmask', '-')
                gateway = ni.gateways().get('default', {}).get(ni.AF_INET, ['-'])[0]
                mac = ni.ifaddresses(iface).get(ni.AF_LINK, [{}])[0].get('addr', '-')
                data.append([iface, ip, netmask, gateway, mac])
        except:
            continue
    return data

def get_dns():
    try:
        with open("/etc/resolv.conf", "r") as f:
            return [line.split()[1] for line in f if line.startswith("nameserver")]
    except:
        return ["-"]

def get_device_name():
    return platform.node()

def get_os_info():
    return f"{platform.system()} {platform.release()} ({platform.machine()})"

def get_fqdn():
    return socket.getfqdn()

def get_ssid():
    try:
        result = subprocess.check_output("iwgetid -r", shell=True).decode().strip()
        return result if result else "-"
    except:
        return "-"
 
def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            seconds = float(f.readline().split()[0])
            return str(timedelta(seconds=int(seconds)))
    except:
        return "-"

def ping_host(host):
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "1", host], stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def is_tool(name):
    return subprocess.call(f"type {name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def get_public_ip():
    try:
        return urllib.request.urlopen('https://api.ipify.org').read().decode()
    except:
        return "-"

def speed_test():
    try:
        import speedtest
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        return f"{download:.2f} Mbps ↓ / {upload:.2f} Mbps ↑"
    except:
        return "-"

def get_active_connections():
    try:
        out = subprocess.check_output("ss -tun | tail -n +2 | wc -l", shell=True).decode().strip()
        return out
    except:
        return "-"

def main():
    clear()
    print(Fore.GREEN + "\n🖥️  sistem:")
    print(f"- hostname     : {get_device_name()}")
    print(f"- fqdn         : {get_fqdn()}")
    print(f"- os           : {get_os_info()}")
    print(f"- uptime       : {get_uptime()}")

    print(Fore.GREEN + "\n📡  interface aktif:")
    data = get_interface_info()
    if data:
        headers = ["Interface", "IP Address", "Netmask", "Gateway", "MAC"]
        print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
        print(f"- total aktif  : {len(data)}")
    else:
        print("- tidak ada interface aktif")

    print(Fore.GREEN + "\n📶  wifi ssid:")
    print(f"- {get_ssid()}")

    print(Fore.GREEN + "\n🌍  ip publik:")
    print(f"- {get_public_ip()}")

    print(Fore.GREEN + "\n🌐  dns server:")
    for dns in get_dns():
        print(f"- {dns}")

    print(Fore.GREEN + "\n📈  tes koneksi:")
    targets = {
        "Gateway": data[0][3] if data else "-",
        "DNS 1": get_dns()[0] if get_dns() else "-",
        "Google": "8.8.8.8"
    }

    for name, ip in targets.items():
        if ip == "-":
            print(f"{name}: {Fore.RED}tidak tersedia")
        else:
            status = ping_host(ip)
            icon = f"{Fore.GREEN}online ✓" if status else f"{Fore.RED}offline ✗"
            print(f"{name} ({ip}): {icon}")

    print(Fore.GREEN + "\n🚀  speedtest:")
    print(f"- {speed_test()}")

    print(Fore.GREEN + "\n🔌  koneksi aktif:")
    print(f"- {get_active_connections()} koneksi (tcp/udp)")

    print(Fore.CYAN + "\n🧪  tools yang dibutuhkan:")
    for tool in ["iwgetid", "ping", "ss"]:
        status = f"{Fore.GREEN}✔ ditemukan" if is_tool(tool) else f"{Fore.RED}✗ tidak ditemukan"
        print(f"- {tool}: {status}")

if __name__ == "__main__":
    main()

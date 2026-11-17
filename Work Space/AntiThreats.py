#C:/Users/elite/AppData/Local/Programs/Python/Python313/python.exe "c:/Users/elite/OneDrive/Desktop/Work Space/AntiThreats.py"
import socket
import select
import json
import logging
import threading
from datetime import datetime
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP
from scapy.config import conf
import re

# 🖍️ Styled console output
def styled_print(message):
    styled = ""
    for char in message:
        styled += "\033[31m" + char + "\033[0m"
    print(styled)

# 🧾 Logging setup
def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

# 🧠 Attack detection validators
def detect_packet_injection(data):
    return bool(re.search(r'suspicious_pattern', data, re.IGNORECASE))

def detect_command_injection(data):
    patterns = [r';\s*(rm|shutdown|exec|wget|curl)', r'\b(eval|os\.system)\b']
    return any(re.search(p, data, re.IGNORECASE) for p in patterns)

def detect_sql_injection(data):
    patterns = [r"(\bSELECT\b|\bDROP\b|\bINSERT\b|\bDELETE\b).*--", r"' OR '1'='1"]
    return any(re.search(p, data, re.IGNORECASE) for p in patterns)

def detect_xss(data):
    return bool(re.search(r'<script.*?>.*?</script>', data, re.IGNORECASE))

def detect_unicode_obfuscation(data):
    return bool(re.search(r'[\u202e\u200f\u200e]', data))

def detect_oversized_payload(data, max_size=8192):
    return len(data.encode("utf-8")) > max_size

# 🧩 Rate limiting tracker
connections = {}
def detect_rate_limiting(address):
    current_time = datetime.now()
    if address not in connections:
        connections[address] = []
    connections[address].append(current_time)
    connections[address] = [time for time in connections[address] if (current_time - time).seconds < 60]

    if len(connections[address]) > 100:
        warning_message = f"Rate limiting alert for {address}"
        logging.warning(warning_message)
        styled_print(warning_message)

# 🛡️ Traffic logger + attack scanner
def log_traffic(protocol, address, data):
    message = f"{protocol} from {address}: {data}"
    logging.info(message)
    styled_print(message)

    alerts = []
    if detect_packet_injection(data): alerts.append("Packet injection")
    if detect_command_injection(data): alerts.append("Command injection")
    if detect_sql_injection(data): alerts.append("SQL injection")
    if detect_xss(data): alerts.append("XSS attempt")
    if detect_unicode_obfuscation(data): alerts.append("Unicode obfuscation")
    if detect_oversized_payload(data): alerts.append("Oversized payload")

    for alert in alerts:
        warning_message = f"{alert} detected from {address}"
        logging.warning(warning_message)
        styled_print(warning_message)

    detect_rate_limiting(address)

# 🧠 Attack summary from logs
def detect_attack(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()

    attack_ips = set()
    attack_methods = {
        'DDoS': [],
        'Phishing': [],
        'Malware': [],
        'Unauthorized Access': []
    }

    for line in lines:
        if "detected" in line:
            parts = line.split(' ')
            ip = parts[-1].strip()
            attack_ips.add(ip)

    for ip in attack_ips:
        styled_print(f"Possible attack from IP: {ip}")

    for method, ips in attack_methods.items():
        styled_print(f"\n{method} Attacks:")
        for ip in ips:
            styled_print(f" - {ip}")

# 📡 Packet callback (captures ALL ports, TCP + UDP)
def packet_callback(packet):
    if packet.haslayer(IP):
        src = packet[IP].src
        dst = packet[IP].dst
        proto = "OTHER"
        sport = None
        dport = None

        if packet.haslayer(TCP):
            proto = "TCP"
            sport = packet[TCP].sport
            dport = packet[TCP].dport
        elif packet.haslayer(UDP):
            proto = "UDP"
            sport = packet[UDP].sport
            dport = packet[UDP].dport

        msg = f"{proto} {src}:{sport} -> {dst}:{dport}"
        log_traffic(proto, f"{src}:{sport}", msg)

# 🚀 IDS bootstrap (no need to bind sockets anymore)
def combined_server(log_file='server_log.txt'):
    setup_logging(log_file)
    logging.info("Sniffer starting...")
    styled_print("Sniffer starting... Listening on ALL ports!")

    # Force L3 sniffing (works without npcap)
    sniff(prn=packet_callback, store=0, iface=conf.iface, L3socket=conf.L3socket)

# 🏁 Entry point
if __name__ == "__main__":
    banner = '██████╗ersonal\n██╔══██╗ortection\n██████╔╝\n██╔═══╝\n██║Sniffer starting...\n╚═╝'
    styled_print(banner)
    combined_server()
    detect_attack('server_log.txt')

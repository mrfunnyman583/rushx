import requests
from scapy.all import *
from collections import Counter
from datetime import datetime

# Define global variables
captured_packets = []

def send_to_discord(webhook_url, data):
    payload = {
        "content": data
    }
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send message to Discord. Status code: {response.status_code}")

def packet_handler(webhook_url, target_ip, target_port, capture_duration=None, verbose=False):
    packet_counts = Counter()
    source_ips = Counter()
    destination_ips = Counter()
    source_ports = Counter()
    destination_ports = Counter()

    start_time = datetime.now()
    
    def process_packet(pkt):
        if IP in pkt and pkt[IP].src == target_ip and pkt[IP].dport == target_port:
            # Process the packet and extract relevant data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            packet_data = f"[{timestamp}] Source IP: {pkt[IP].src}, Destination IP: {pkt[IP].dst}, Source Port: {pkt[TCP].sport}, Destination Port: {pkt[TCP].dport}"
            send_to_discord(webhook_url, packet_data)
            if verbose:
                print(packet_data)

            # Update traffic statistics
            packet_counts["Total Packets"] += 1
            source_ips[pkt[IP].src] += 1
            destination_ips[pkt[IP].dst] += 1
            source_ports[pkt[TCP].sport] += 1
            destination_ports[pkt[TCP].dport] += 1

            # Capture packets
            captured_packets.append(packet_data)

            # Check if capture duration is reached
            if capture_duration and (datetime.now() - start_time).total_seconds() >= capture_duration:
                raise KeyboardInterrupt

    def print_traffic_stats():
        print("\nTraffic Summary:")
        print(f"Total Packets: {packet_counts['Total Packets']}")
        print(f"Source IPs: {', '.join(source_ips.keys())}")
        print(f"Destination IPs: {', '.join(destination_ips.keys())}")
        print(f"Source Ports: {', '.join(map(str, source_ports.keys()))}")
        print(f"Destination Ports: {', '.join(map(str, destination_ports.keys()))}")

    return process_packet, print_traffic_stats

def main():
    # Get user input for Discord webhook URL, target IP, target port, and capture duration
    webhook_url = input("Enter the Discord webhook URL: ")
    target_ip = input("Enter the target IP address: ")
    target_port = int(input("Enter the target port: "))
    capture_duration = int(input("Enter capture duration (seconds, 0 for continuous capture): "))
    verbose = input("Enable verbose mode? (yes/no): ").lower() == "yes"

    process_packet, print_traffic_stats = packet_handler(
        webhook_url, target_ip, target_port, capture_duration, verbose)
    
    try:
        # Start capturing packets on eth0
        print("Monitoring traffic. Press Ctrl-C to stop.")
        sniff(iface="eth0", prn=process_packet, filter=f"host {target_ip} and port {target_port}")
    except KeyboardInterrupt:
        print("\nTraffic monitoring stopped.")
        print_traffic_stats()

    # Save captured packets to a file
    with open("captured_packets.txt", "w") as f:
        f.write("\n".join(captured_packets))

if __name__ == "__main__":
    main()

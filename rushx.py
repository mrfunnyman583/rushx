import argparse
import configparser
import os
import socket
import requests
import subprocess

class Rushx:
    def __init__(self):
        # Initialize argument parser
        self.parser = argparse.ArgumentParser(description="rushx - A tool for various terminal tasks.")
        self.parser.add_argument(
            "command",
            help="The command to execute",
            choices=["send", "info", "scan", "config", "list", "remove", "edit", "packages", "system_info"]
        )
        self.parser.add_argument("--content", help="Message content for 'send' command")
        self.parser.add_argument("--ip", help="IP address for 'info' and 'scan' commands")
        self.parser.add_argument("--url", help="Webhook URL for 'config' and 'edit' commands")
        self.args = self.parser.parse_args()

        # Load configuration
        self.config_file = "config.ini"
        self.webhook_url = None
        self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if "rushx" in config:
                self.webhook_url = config["rushx"].get("webhook_url")

    def execute_command(self):
        if self.args.command == "send":
            content = self.args.content
            self.send_message_content(content)
        elif self.args.command == "info":
            ip_address = self.args.ip
            self.get_ip_info(ip_address)
        elif self.args.command == "scan":
            ip_address = self.args.ip
            self.scan_ip(ip_address)
        elif self.args.command == "config":
            url = self.args.url
            self.configure_webhook_url(url)
        elif self.args.command == "list":
            self.list_configurations()
        elif self.args.command == "remove":
            name = self.args.remove
            self.remove_configuration(name)
        elif self.args.command == "edit":
            url = self.args.url
            self.edit_webhook_url(url)
        elif self.args.command == "packages":
            self.check_required_packages()
        elif self.args.command == "system_info":
            self.get_system_info()
        else:
            print("Invalid command. Use 'help' to see available commands.")

    def send_message_content(self, message_content):
        if self.webhook_url:
            headers = {"Content-Type": "application/json"}
            payload = {"content": message_content}

            # Debug: Print the message content
            print("Message Content:")
            print(message_content)

            response = requests.post(self.webhook_url, headers=headers, json=payload)

            if response.status_code == 200:
                print("Message sent to Discord successfully.")
            else:
                print(f"Failed to send message to Discord. Status code: {response.status_code}")
        else:
            print("Discord webhook URL is not configured. Use 'config' command to set it.")

    def get_ip_info(self, ip_address):
        # Fetch IP info from ipinfo.io
        ip_info_url = f"https://ipinfo.io/{ip_address}/json"
        response = requests.get(ip_info_url)

        if response.status_code == 200:
            ip_info = response.json()
            print(f"IP Information for {ip_address}:")
            for key, value in ip_info.items():
                print(f"{key}: {value}")
        else:
            print(f"Failed to fetch IP information for {ip_address}. Status code: {response.status_code}")

    def scan_ip(self, ip_address):
        # Implement scanning IP functionality
        try:
            # Example: Ping the IP address
            response = subprocess.check_output(["ping", "-c", "4", ip_address])
            print(f"Scan result for {ip_address}:\n{response.decode('utf-8')}")
        except subprocess.CalledProcessError:
            print(f"Unable to scan {ip_address}. Check the IP address or scanning tool.")

    # Implement the rest of the commands and features here

    def run(self):
        self.execute_command()

if __name__ == "__main__":
    rushx = Rushx()
    rushx.run()

import argparse
import configparser
import os
import socket
import requests
import subprocess
import json

class Rushx:
    def __init__(self):
        # Initialize argument parser
        self.parser = argparse.ArgumentParser(description="rushx - A tool for various terminal tasks.")
        self.parser.add_argument(
            "command",
            help="The command to execute",
            choices=["send", "info", "scan", "config", "list", "remove", "edit", "packages", "system_info", "test"]
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
            self.edit_webhook_url(url)
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
        elif self.args.command == "test":
            self.send_test_message()
        else:
            print("Invalid command. Use 'help' to see available commands.")

    def send_message_content(self, message_content):
        if self.webhook_url:
            headers = {"Content-Type": "application/json"}
            payload = {"content": message_content}

            response = requests.post(self.webhook_url, headers=headers, json=payload)

            if response.status_code == 204:
                print("Message sent to Discord successfully.")
                print("(Note: error 204's can be false-positive)")
            else:
                print(f"Failed to send message to Discord. Status code: {response.status_code}")
        else:
            print("Discord webhook URL is not configured. Use 'config' command to set it.")

    def get_ip_info(self, ip_address):
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        if response.status_code == 200:
            ip_info = json.loads(response.text)
            info_message = f"IP Information for {ip_address}:\n"
            for key, value in ip_info.items():
                info_message += f"{key}: {value}\n"
            self.send_message_content(info_message)
        else:
            print(f"Failed to fetch IP information for {ip_address}. Status code: {response.status_code}")

    def scan_ip(self, ip_address):
        try:
            result = subprocess.check_output(["nmap", "-F", ip_address])
            print(result.decode("utf-8"))
        except subprocess.CalledProcessError:
            print("Failed to scan IP address.")

    def edit_webhook_url(self, url):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if "rushx" in config:
                config["rushx"]["webhook_url"] = url
                with open(self.config_file, "w") as configfile:
                    config.write(configfile)
                print("Webhook URL updated.")
            else:
                print("Configuration section 'rushx' not found.")
        else:
            print("Config file does not exist. Create a configuration using 'config' command.")

    def list_configurations(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            print("Configurations:")
            for section_name in config.sections():
                print(f"Section: {section_name}")
                for key, value in config[section_name].items():
                    print(f"{key}: {value}")

    def remove_configuration(self, name):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if "rushx" in config and name in config["rushx"]:
                del config["rushx"][name]
                with open(self.config_file, "w") as configfile:
                    config.write(configfile)
                print(f"Configuration '{name}' removed.")
            else:
                print(f"Configuration '{name}' not found.")

    def check_required_packages(self):
        try:
            required_packages = ["nmap", "requests"]
            missing_packages = []

            for package in required_packages:
                subprocess.check_output(["pip", "show", package])
            print("All required packages are installed.")

        except subprocess.CalledProcessError:
            print("Some required packages are missing. Installing...")

            for package in required_packages:
                try:
                    subprocess.check_output(["pip", "install", package])
                except subprocess.CalledProcessError:
                    missing_packages.append(package)

            if missing_packages:
                print(f"Failed to install the following packages: {', '.join(missing_packages)}")
            else:
                print("All required packages are now installed.")

    def get_system_info(self):
        system_info = {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor":

import requests
import json
import socket
import os
import logging
import getpass
import configparser
import argparse
import importlib
import subprocess

class Rushx:
    def __init__(self):
        self.check_dependencies()
        self.webhook_url = None
        self.log_file = "rushx.log"
        self.config_file = "rushx.ini"
        self.setup_logging()
        self.load_config()
        self.setup_cli()

    def check_dependencies(self):
        required_packages = ['requests', 'socket', 'configparser', 'argparse', 'importlib']
        missing_packages = []

        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print("The following required packages are missing:")
            for package in missing_packages:
                print(f"- {package}")

            install = input("Do you want to install them now? (yes/no): ").lower()
            if install == "yes":
                for package in missing_packages:
                    subprocess.run(["pip", "install", package])
            else:
                print("Exiting the program as required packages are not installed.")
                exit()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def log(self, message):
        logging.info(message)

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if "rushx" in config:
                self.webhook_url = config["rushx"].get("webhook_url")

    def save_config(self):
        config = configparser.ConfigParser()
        config["rushx"] = {"webhook_url": self.webhook_url}
        with open(self.config_file, "w") as configfile:
            config.write(configfile)

    def setup_cli(self):
        parser = argparse.ArgumentParser(description="rushx - Discord Webhook and IP Tool")
        parser.add_argument("command", choices=["send", "info", "scan", "config", "list", "remove", "edit"], help="Command to execute")
        parser.add_argument("--content", help="Message content for 'send' command")
        parser.add_argument("--repeat", action="store_true", help="Repeat 'send' command")
        parser.add_argument("--interval", type=int, default=10, help="Interval in seconds between messages (used with --repeat)")
        parser.add_argument("--ip", help="IP address for 'info' or 'scan' command")
        parser.add_argument("--port", type=int, help="Port number for 'scan' command")
        parser.add_argument("--url", help="Discord webhook URL for 'config' and 'edit' commands")
        parser.add_argument("--list", action="store_true", help="List saved configurations for 'list' command")
        parser.add_argument("--remove", help="Remove a saved configuration by name for 'remove' command")

        self.args = parser.parse_args()

    def execute_command(self):
        if self.args.command == "send":
            content = self.args.content or input("Enter the message content you want to send: ")
            if self.send_test_message(content):
                self.log("Webhook test message sent successfully!")
                if self.args.repeat:
                    interval = self.args.interval
                    while True:
                        if not self.send_test_message(content):
                            self.log("Failed to send a test message to the webhook.")
                        import time
                        time.sleep(interval)
                return

        elif self.args.command == "info":
            ip = self.args.ip or input("Enter an IP address to get information: ")
            ip_info = self.get_ip_info(ip)

            if ip_info:
                self.log("IP Information:")
                for key, value in ip_info.items():
                    print(f"{key}: {value}")
            else:
                self.log("Failed to retrieve IP information.")
            return

        elif self.args.command == "scan":
            ip = self.args.ip or input("Enter an IP address to scan: ")
            port = self.args.port or int(input("Enter a port to scan: "))

            if self.port_scan(ip, port):
                self.log(f"Port {port} is open on {ip}.")
            else:
                self.log(f"Port {port} is closed on {ip}.")
            return

        elif self.args.command == "config":
            url = self.args.url or input("Enter the Discord webhook URL: ")
            self.webhook_url = url
            self.save_config()
            self.log("Webhook URL saved successfully.")
            return

        elif self.args.command == "list":
            config = configparser.ConfigParser()
            config.read(self.config_file)
            if "rushx" in config:
                for name, value in config["rushx"].items():
                    print(f"{name}: {value}")
            return

        elif self.args.command == "remove":
            name = self.args.remove
            config = configparser.ConfigParser()
            config.read(self.config_file)
            if "rushx" in config and name in config["rushx"]:
                del config["rushx"][name]
                with open(self.config_file, "w") as configfile:
                    config.write(configfile)
                self.log(f"Configuration '{name}' removed successfully.")
            return

        elif self.args.command == "edit":
            url = self.args.url or input("Enter the new Discord webhook URL: ")
            self.webhook_url = url
            self.save_config()
            self.log("Webhook URL edited and saved successfully.")
            return

        else:
            self.log("Invalid command. Use 'send', 'info', 'scan', 'config', 'list', 'remove', or 'edit'.")

    def send_test_message(self, content):
        if self.webhook_url:
            message = {"content": content}
            headers = {"Content-Type": "application/json"}

            response = requests.post(self.webhook_url, data=json.dumps(message), headers=headers)

            if response.status_code == 204:
                return True

        return False

    def get_ip_info(self, ip):
        url = f"https://ipinfo.io/{ip}/json"
        headers = {"Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                ip_info = response.json()
                return ip_info
        except Exception as e:
            self.log(f"Failed to retrieve IP information: {str(e)}")

        return None

    def port_scan(self, ip, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip, port))
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False

    def run(self):
        self.execute_command()

if __name__ == "__main__":
    rushx = Rushx()
    rushx.run()

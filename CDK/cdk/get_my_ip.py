import requests


class MyIP:
    def __init__(self):
        self.url = 'https://api.ipify.org?format=json'

    def get(self) -> str:
        response = requests.get(self.url)
        public_ip = response.json()['ip']
        print("Public IP Address:", public_ip)
        return str(public_ip)

    def get_ip_cidr(self) -> str:
        public_ip_cidr = self.get() + "/32"
        print("Public IP Address:", public_ip_cidr)
        return public_ip_cidr

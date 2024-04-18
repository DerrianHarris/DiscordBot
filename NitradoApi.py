import os
import random
import time
import re
import requests
from dotenv import load_dotenv
from rcon.source import Client

load_dotenv()


class NitradoApi:
    def __init__(self):
        self.NITRADO_TOKEN = os.getenv("NITRADO_TOKEN")
        self.SERVER_ID = os.getenv("SERVER_ID")
        self.RCON_IP_FULL = os.getenv("RCON_IP_FULL")
        split = self.RCON_IP_FULL.split(":")
        self.RCON_PWD = os.getenv("RCON_PWD")
        self.RCON_IP = split[0]
        self.RCON_PORT = int(split[1])
        self.status_codes = {
            "started": "Started",
            "stopped": "Stopped",
            "stopping": "Stopping",
            "restarting": "Restarting",
            "suspended": "suspended",
            "guardian_locked": "Locked",
            "gs_installation": "Updating",
            "backup_restore": "Restoring Backup",
            "backup_creation": "Creating Backup",
            "chunkfix": "Runnign Minecraft chunkfix",
            "overviewmap_render": "Running Minecraft Overview Map rendering",
        }
        pass

    async def get_server_status(self):
        print("Getting Server Status")
        response = requests.get(
            f"https://api.nitrado.net/services/{self.SERVER_ID}/gameservers",
            auth=BearerAuth(self.NITRADO_TOKEN),
        )
        print("Status Code: " + str(response.status_code))
        print("Response: " + str(response.content))
        response_json = response.json()
        if response.status_code == 200:
            status = response_json["data"]["gameserver"]["status"]
            if status in self.status_codes:
                status = self.status_codes[status]
        else:
            status = response_json["message"]
        return status

    async def stop_server(self):
        print("Stopping Server")
        response = requests.post(
            f"https://api.nitrado.net/services/{self.SERVER_ID}/gameservers/stop",
            auth=BearerAuth(self.NITRADO_TOKEN),
        )
        print("Status Code: " + str(response.status_code))
        print("Response: " + str(response.content))
        response_json = response.json()
        status = response_json["message"]
        return status

    async def start_server(self, game="arksa"):
        print("Starting Server for " + game)
        payload = {"game": game}
        response = requests.post(
            f"https://api.nitrado.net/services/{self.SERVER_ID}/gameservers/games/start",
            auth=BearerAuth(self.NITRADO_TOKEN),
            params=payload,
        )
        print("Status Code: " + str(response.status_code))
        print("Response: " + str(response.content))
        response_json = response.json()
        status = response_json["message"]
        return status

    async def safe_start_server(self, game="arksa"):
        print("Running safe server start")
        server_status = self.get_server_status()
        if server_status.lower() in ["stopped"]:
            status = self.stop_server()
        else:
            status = "Cannot stop server! Current server status: " + server_status
        return status

    async def safe_stop_server(self):
        print("Running safe server stop")
        server_status = self.get_server_status()
        if server_status.lower() in ["started"]:
            status = self.stop_server()
        else:
            status = "Cannot stop server! Current server status: " + server_status
        return status

    async def uninstall_game(self, game="arksa"):
        print("Uninstalling game for " + game)
        payload = {"game": game}
        response = requests.delete(
            f"https://api.nitrado.net/services/{self.SERVER_ID}/gameservers/games/uninstall",
            auth=BearerAuth(self.NITRADO_TOKEN),
            params=payload,
        )
        print("Status Code: " + str(response.status_code))
        print("Response: " + str(response.content))
        response_json = response.json()
        status = response_json["message"]
        return status

    async def restart_server(
        self, message="Restarting...", restart_message="Restarting..."
    ):
        print("Restarting Server")
        payload = {"message": message, "restart_message": restart_message}
        response = requests.post(
            f"https://api.nitrado.net/services/{self.SERVER_ID}/gameservers/restart",
            auth=BearerAuth(self.NITRADO_TOKEN),
            params=payload,
        )
        print("Status Code: " + str(response.status_code))
        print("Response: " + str(response.content))
        response_json = response.json()
        status = response_json["message"]
        return status

    async def run_console_command(self, command=""):
        print("Running command on Server: " + command)
        with Client(self.RCON_IP, self.RCON_PORT, passwd=self.RCON_PWD) as client:
            try:
                response = client.run(command)
            except Exception as e:
                print(e)
            else:
                return response
        return None


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

import requests
from pathlib import Path

def connect(endpoint, port):
    client = Client(endpoint, port)
    return client

class Client():
    def __init__(self, endpoint, port):
        self.endpoint = f"{endpoint}:{port}/api/v0"
        self.add_query = "?pin=True&quieter=True"

        errors = self.check_connection()
        if errors:
            raise Exception(errors)

    def check_connection(self):
        request_url = f"{self.endpoint}/id"
        try:
            response = requests.post(request_url, timeout=5)
            if response.status_code != 200:
                return (f"Could not connect to {request_url}")
        except Exception as e:
            return repr(e)

    def get(self, hash: str) -> bytes:
        request_url = f"{self.endpoint}/get?arg={hash}"
        response = requests.post(request_url)
        if response.status_code == 200:
            return response.text
        raise Exception(f"request failed with status code {response.status_code} and error: {response.text}")

    def add_file(self, path: str) -> str:
        absolute_path = Path(path)
        if not absolute_path.exists() or not absolute_path.is_file():
            raise Exception("file doesn't exist")
        request_url = f"{self.endpoint}/add{self.add_query}"
        file = {
            "files": open(
                absolute_path,
                "rb",
            )
        }
        print(request_url)
        response = requests.post(request_url, files=file).json()
        return response['Hash']
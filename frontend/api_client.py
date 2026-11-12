import requests

from frontend.config import API_URL


class APIClient:

    def __init__(self, token=None):

        self.base_url = API_URL
        self.session = requests.Session()

        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })

    def get(self, endpoint):

        response = self.session.get(
            f"{self.base_url}{endpoint}",
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def post(self, endpoint, data=None):

        response = self.session.post(
            f"{self.base_url}{endpoint}",
            json=data,
            timeout=180
        )

        response.raise_for_status()

        return response.json()

    def upload(self, endpoint, file):

        response = self.session.post(
            f"{self.base_url}{endpoint}",
            files={
                "file": (
                    file.name,
                    file.getvalue(),
                    file.type
                )
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json()
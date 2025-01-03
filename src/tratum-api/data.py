"""Tratum Python API."""
import requests

class TratumAPI:
    def __init__(self, tratum_username: str, tratum_password: str):
        """__init__

        Args:
            tratum_username (str): Username for Tratum API.
            tratum_password (str): Password for Tratum API.
        """
        self.tratum_username = tratum_username
        self.tratum_password = tratum_password

    def get_token(self, email: str, password: str):
        """Generate API token.

        Args:
            email (str): Tratum API account e-mail.
            password (str): Tratum API account password.

        Returns:
            str: API token.
        """
        url = "https://search.tratum.com.br/v1/login"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "password": password,
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()['token']

    def get_process_detail(
        self, token: str, organization_id: str, process_number: str):
        url = "https://search.tratum.com.br/v1/process/{organization_id}/{process_number}".format(
            organization_id=organization_id,
            process_number=process_number,
        )
        headers = {
            'Authorization': 'Bearer {token}'.format(token=token)
        }
        response = requests.get(url, headers=headers)

"""Tratum Python API."""
import requests

class TratumAPI:
    def __init__(self, tratum_email: str, tratum_password: str):
        """__init__.

        Args:
            tratum_email (str): E-mail for Tratum API.
            tratum_password (str): Password for Tratum API.
        """
        url = "https://search.tratum.com.br/v1/login"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "email": tratum_email,
            "password": tratum_password,
        }
        response = requests.post(url, headers=headers, json=data)
        self.token = response.json()['token']

    def get_process_detail(
        self, token: str, organization_id: str, process_number: str):
        url = "https://search.tratum.com.br/v1/process/{organization_id}/{process_number}".format(
            organization_id=organization_id,
            process_number=process_number,
        )
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)
        }
        response = requests.get(url, headers=headers)

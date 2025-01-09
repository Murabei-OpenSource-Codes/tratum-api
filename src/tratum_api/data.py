"""Tratum Python API."""
import requests

class TratumAPI:
    def __init__(
        self,
        tratum_email: str,
        tratum_password: str,
        organization_id: int,
        holder_id: int):
        """__init__.

        Args:
            tratum_email (str): E-mail for Tratum API.
            tratum_password (str): Password for Tratum API.
            organization_id (int): Organization ID in Tratum API.
            holder_id (int): Holder ID in Tratum API.
        """
        # Set global variables
        self.organization_id = organization_id
        self.holder_id = holder_id

        # Fetch token
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

    def get_process_detail(self, process_number: str):
        """Fetch process details in Tratum API.

        Args:
            process_number (str): Process document.
        """
        url = "https://search.tratum.com.br/v1/process/{organization_id}/{process_number}".format(
            organization_id=self.organization_id,
            process_number=process_number,
        )
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def download_process_document(self, document_url: str):
        """Download pdf file from process.

        Args:
            document_url (str): Url pointing to pdf.
        """
        url = "https://search.tratum.com.br/v1/url?page={document_url}".format(document_url=document_url)
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)
        }
        response = requests.get(url, headers=headers)
        return response.text

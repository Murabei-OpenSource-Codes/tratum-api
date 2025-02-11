"""Tratum Python API."""
import requests
from tratum_api.exceptions import (
    TratumAPIProblemAPIException,
    TratumAPIInvalidDocumentException,
    TratumAPIInvalidS3UrlException)

class TratumAPI:
    def __init__(
        self,
        tratum_email: str,
        tratum_password: str,
        organization_id: int,
        holder_id: int,
        cnpj: str):
        """__init__.

        Args:
            tratum_email (str): E-mail for Tratum API.
            tratum_password (str): Password for Tratum API.
            organization_id (int): Organization ID in Tratum API.
            holder_id (int): Holder ID in Tratum API.
            cnpj (str): Organization document.
        """
        # Set global variables
        self.organization_id = organization_id
        self.holder_id = holder_id
        self.cnpj = cnpj

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

    def is__process_number__valid(self, process_number: str):
        """Check process number validation.

        - Must have exactly 20 digits.
        - First 7 digits must follow a specific sequence.
        - Last 2 digits (verification digits) must be validated based on
        initial sequence.

        Args:
            process_number (str): process number to be validated.

        Returns:
            bool: Wether process number is valid.
        """
        numbers = [int(digit) for digit in process_number if digit.isdigit()]
        if len(numbers) != 20:
            return False

        numbers = ''.join(str(num) for num in numbers)
        sequencial = numbers[:7]
        digito_verificador = numbers[7:9]
        restante = numbers[9:]

        # Calcula o DV esperado
        numero_sem_dv = sequencial + restante
        resto = int(numero_sem_dv) * 100 % 97
        dv = 98 - resto
        dv_calculado = f"{dv:02d}"

        if digito_verificador != dv_calculado:
            return False

        return True

    def monitor_process(self, process_number: str):
        """Send process to monitoring.

        Args:
            process_number (str): Process document.
        """
        url = "https://search.tratum.com.br/v2/importProcess/{organization_id}/{process_number}/?document={cnpj}".format(
            organization_id=self.organization_id,
            process_number=process_number,
            cnpj=self.cnpj
        )
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)
        }
        response = requests.post(url, headers=headers, json={})
        response_json = response.json()
        if response.status_code != 200 or response_json['status'] != 'sucess':
            raise TratumAPIProblemAPIException(
                message="error related to internal problems in APIs "
                        "or services.",
                payload={
                    "status_code": response.status_code,
                    "status_description": response_json['status']
                }
            )
        elif response_json['process']['status'] == 'INVALID':
            raise TratumAPIInvalidDocumentException(
                message="invalid process number",
                payload={
                    "process_number": process_number,
                }
            )
        else:
            return response_json

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
        response_json = response.json()
        if response.status_code != 200:
            raise TratumAPIProblemAPIException(
                message="error related to internal problems in APIs "
                        "or services.",
                payload={
                    "status_code": response.status_code,
                    "status_description": response_json['status']
                }
            )
        elif not self.is__process_number__valid(process_number):
            raise TratumAPIInvalidDocumentException(
                message="invalid process number",
                payload={
                    "process_number": process_number,
                }
            )

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
        s3_url = response.text
        print(self.is__s3_url__valid(s3_url))
        if response.status_code != 200:
            raise TratumAPIProblemAPIException(
                message="error related to internal problems in APIs "
                        "or services.",
                payload={
                    "status_code": response.status_code,
                }
            )
        elif not self.is__s3_url__valid(s3_url):
            raise TratumAPIInvalidS3UrlException(
                message="invalid s3 url.",
                payload={"s3_url": s3_url}
            )
        else:
            return s3_url


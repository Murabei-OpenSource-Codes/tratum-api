"""Tratum Python API."""
import os
import requests
from tratum_api.exceptions import (
    TratumAPILoginError, TratumAPIProblemAPIException,
    TratumAPIInvalidDocumentException)


class TratumAPI:
    """Tratum API to help comunication with end-points."""

    def __init__(self, tratum_email: str, tratum_password: str,
                 organization_id: int, holder_id: int, cnpj: str,
                 proxy: str = None):
        """__init__.

        Args:
            tratum_email (str):
                E-mail for Tratum API.
            tratum_password (str):
                Password for Tratum API.
            organization_id (int):
                Organization ID in Tratum API.
            holder_id (int):
                Holder ID in Tratum API.
            cnpj (str):
                Organization document.
            proxy (str): = None
                Proxy server for end-point calls.
        """
        #
        if proxy is None:
            proxy = os.getenv('TRATUM_API_PROXY')
        self._proxy = proxy
        self._requests_proxies = {
          "http": self._proxy, "https": self._proxy}

        # Create a Session object and set proxy
        self.session = requests.Session()
        self.session.proxies = self._requests_proxies

        # Set global variables
        self.organization_id = organization_id
        self.holder_id = holder_id
        self.cnpj = cnpj

        # Store credentials if token is expired
        self._tratum_email = tratum_email
        self._tratum_password = tratum_password

        # Login to application
        self.login()

    def login(self):
        """Login at Tratum API.

        Uses attributes `_tratum_email` and `_tratum_password` to login
        at Tratum and retrive token.
        """
        url = "https://search.tratum.com.br/v1/login"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "email": self._tratum_email,
            "password": self._tratum_password}

        try:
            response = self.session.post(
                url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
        except Exception:
            status_code = response.status_code
            response_text = response.text
            msg = (
                "Error when loggin to TratumAPI.\n"
                "status_code: [{status_code}]").format(status_code=status_code)
            raise TratumAPILoginError(
                msg, payload={
                    "status_code": status_code,
                    "response_payload": response_text})
        self.token = response.json()['token']
        return True

    def is__process_number__valid(self, process_number: str):
        """Check process number validation.

        - Must have exactly 20 digits.
        - First 7 digits must follow a specific sequence.
        - Last 2 digits (verification digits) must be validated based on
        initial sequence.

        Args:
            process_number (str):
                process number to be validated.

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
            process_number (str):
                Process document.
        """
        url = (
            "https://search.tratum.com.br/v2/importProcess/" +
            "{organization_id}/{process_number}/?document={cnpj}").format(
            organization_id=self.organization_id,
            process_number=process_number,
            cnpj=self.cnpj)
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)}
        try:
            response = self.session.post(url, headers=headers, json={})
            response.raise_for_status()
        except Exception:
            response_json = response.json()
            obs = response_json.get('obs', "")
            msg = (
                "Error related to internal problems in APIs "
                "or services. Tratum message [{obs}]").format(obs=obs)
            raise TratumAPIProblemAPIException(
                message=msg, payload={
                    "process_number": process_number,
                    "status_code": response.status_code,
                    "response_payload": response_json})

        response_json = response.json()
        # Invalid and other errors at processing are returned with status
        # 200 at the API, but are results of errors. It is necessary to
        # treat using the payload
        # Get if returned status is Ok
        is_status_ok = (
            response_json.get('status', None)
            not in ['sucess', 'processing'])
        if is_status_ok:
            obs = response_json.get('obs', "")
            msg = (
                "Error related to internal problems in APIs "
                "or services. Tratum message:\n[{obs}]").format(obs=obs)
            raise TratumAPIProblemAPIException(
                message=msg, payload={
                    "process_number": process_number,
                    "status_code": response.status_code,
                    "response_payload": response_json})

        # Get if process is INVALID
        is_process_invalid = (
            response_json.get('process', {}).get('status', None) == 'INVALID')
        if is_process_invalid:
            msg = "Invalid process number"
            raise TratumAPIInvalidDocumentException(
                message=msg, payload={
                    "process_number": process_number,
                    "response_payload": response_json
                })

        # If passed the tests, it will be returned as valid response
        return response_json

    def get_process_detail(self, process_number: str):
        """Fetch process details in Tratum API.

        Args:
            process_number (str):
                Process document.
        """
        url = (
            "https://search.tratum.com.br/v1/" +
            "process/{organization_id}/{process_number}").format(
            organization_id=self.organization_id,
            process_number=process_number,
        )
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)
        }
        response = self.session.get(url, headers=headers)
        response_json = response.json()
        if response.status_code != 200:
            raise TratumAPIProblemAPIException(
                message="error related to internal problems in APIs "
                        "or services.",
                payload={
                    "status_code": response.status_code,
                    "status_description": response_json.get('status', None)
                }
            )
        elif not self.is__process_number__valid(process_number):
            raise TratumAPIInvalidDocumentException(
                message="invalid process number",
                payload={
                    "process_number": process_number,
                }
            )
        else:
            return response_json

    def get_process_document_url(self, document_url: str) -> str:
        """Get a authenticated url to download the document.

        Args:
            document_url (str):
                Url pointing to pdf.

        Returns:
            Return the AWS S3 authenticated URL.
        """
        url = "https://search.tratum.com.br/v1/url?page={document_url}"\
            .format(document_url=document_url)
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)
        }
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
        except Exception:
            raise TratumAPIProblemAPIException(
                message="error related to internal problems in APIs "
                        "or services.",
                payload={
                    "status_code": response.status_code,
                }
            )

        s3_url = response.text
        return s3_url

    def download_process_document(self, document_url: str) -> bytes:
        """Download pdf file from process.

        Args:
            document_url (str):
                Url pointing to pdf.

        Returns:
            Return the content of the document at the URL.
        """
        authenticated_url = self.get_process_document_url(
            document_url=document_url)
        try:
            response = self.session.get(authenticated_url)
            response.raise_for_status()
        except Exception:
            msg = (
                "Error when downloading file from AWS. Status code: "
                "[{status_code}]").format(status_code=response.status_code)
            raise TratumAPIProblemAPIException(
                message=msg,
                payload={"status_code": response.status_code})
        return response.content

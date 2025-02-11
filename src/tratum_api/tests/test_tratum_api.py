"""Test Tratum API."""
import os
import unittest
from tratum_api.data import TratumAPI
from tratum_api.exceptions import (
    TratumAPIException,
    TratumAPIProblemAPIException,
    TratumAPIInvalidDocumentException
)
tratum_email = os.getenv("TRATUM_EMAIL")
tratum_password = os.getenv("TRATUM_PASSWORD")
organization_id = os.getenv("ORGANIZATION_ID")
holder_id = os.getenv("HOLDER_ID")

class TestNeuronLabAPI(unittest.TestCase):
    """Test Neuron Lab api."""
    def setUp(self):
        self.tratum_api = TratumAPI(
            tratum_email=tratum_email,
            tratum_password=tratum_password,
            organization_id=organization_id,
            holder_id=holder_id,
            cnpj="33009911000139",
        )

    def test1__monitor_valid_process(self):
        process_number = "10045683220184013400"
        monitored_process = self.tratum_api.monitor_process(
            process_number=process_number)

    def test2__monitor_invalid_process(self):
        process_number = "00000000000000000000"
        with self.assertRaises(TratumAPIInvalidDocumentException) as context:
            self.tratum_api.monitor_process(
                process_number=process_number)
        self.assertEqual(
            str(context.exception),
            "TratumAPIInvalidDocumentException: invalid process number")

    def test3__process_valid_detail(self):
        process_number = "10045683220184013400"
        process_details = self.tratum_api.get_process_detail(
            process_number=process_number)

    def test4__process_invalid_detail(self):
        process_number = "00000000000000000000"
        with self.assertRaises(TratumAPIInvalidDocumentException) as context:
            self.tratum_api.get_process_detail(
                process_number=process_number)
        self.assertEqual(
            str(context.exception),
            "TratumAPIInvalidDocumentException: invalid process number")

    def test5__download_process_document(self):
        document_url = (
            "Processos/401/10045683220184013400/PJETRF1/nao-concedida-a-antecipacao-de-tutela-07-07-2018-15-43.pdf"
        )
        pdf_url = self.tratum_api.download_process_document(
            document_url=document_url)

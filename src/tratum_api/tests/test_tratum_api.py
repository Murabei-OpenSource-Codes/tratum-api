"""Test Tratum API."""
import os
import unittest
from tratum_api.data import TratumAPI

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
            holder_id=holder_id
        )

    def test1__process_detail(self):
        process_number = "10045683220184013400"
        process_details = self.tratum_api.get_process_detail(
            process_number=process_number)
        print(process_details)

    def test2__download_process_document(self):
        document_url = (
            "Processos/401/10045683220184013400/PJETRF1/nao-concedida-a-antecipacao-de-tutela-07-07-2018-15-43.pdf"
        )
        pdf_url = self.tratum_api.download_process_document(
            document_url=document_url)
        print(pdf_url)

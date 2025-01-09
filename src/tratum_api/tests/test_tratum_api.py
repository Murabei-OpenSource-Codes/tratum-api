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

    def test__process_detail(self):
        process_number = "00174885420154036100"
        process_details = self.tratum_api.get_process_detail(
            process_number=process_number)
        print(process_details)

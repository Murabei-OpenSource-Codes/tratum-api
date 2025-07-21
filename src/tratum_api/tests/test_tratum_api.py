"""Test Tratum API."""
import os
import unittest
from tratum_api.data import TratumAPI
from tratum_api.exceptions import (
    TratumAPIInvalidDocumentException, TratumAPILoginError)

tratum_email = os.getenv("TRATUM_EMAIL")
tratum_password = os.getenv("TRATUM_PASSWORD")
organization_id = os.getenv("ORGANIZATION_ID")
holder_id = os.getenv("HOLDER_ID")
cnpj = os.getenv("CNPJ")
valid_process_number = os.getenv("VALID_PROCESS_IN_TRATUM")


class TestNeuronLabAPI(unittest.TestCase):
    """Test Neuron Lab api."""

    def test__login(self):
        """Test correct login."""
        tratum_api = TratumAPI(
            tratum_email=tratum_email, tratum_password=tratum_password,
            organization_id=organization_id, holder_id=holder_id,
            cnpj=cnpj)
        return tratum_api

    def test__login_error(self):
        """Test correct raise when password is incorrect."""
        # Random process to test API
        with self.assertRaises(TratumAPILoginError):
            TratumAPI(
                tratum_email=tratum_email, tratum_password='wrong-pass', # NOQA
                organization_id=organization_id, holder_id=holder_id,
                cnpj=cnpj)

    def test__monitor_valid_process(self):
        """Test monitor valid process end-point."""
        # Random process to test API
        tratum_api = self.test__login()

        process_number = "19777928520247108243"
        monitored_process = tratum_api.monitor_process(
            process_number=process_number)
        self.assertEqual(monitored_process['status'], 'processing')

    def test__monitor_invalid_process(self):
        """Test invalid process monitor."""
        tratum_api = self.test__login()

        # Random process to test API
        process_number = "00000000000000000000"
        with self.assertRaises(TratumAPIInvalidDocumentException) as context:
            tratum_api.monitor_process(
                process_number=process_number)
        self.assertEqual(
            str(context.exception),
            "TratumAPIInvalidDocumentException: Invalid process number")

    def test__process_valid_detail(self):
        """Test invalid process monitor error."""
        tratum_api = self.test__login()

        # Random process to test API
        process_number = valid_process_number
        process_details = tratum_api.get_process_detail(
            process_number=process_number)
        self.assertListEqual(
            list(process_details.keys()),
            [
                "process", "state", "id", "resource", "has_resource",
                "external_code", "classe", "last_class_message", "court",
                "counrt_type", "value_claim", "value_claim_str",
                "range_value_claim", "court_name", "judging_organ",
                "status", "status_custom", "distribution_date",
                "distribution_date_format", "year_distribution_date",
                "month_distribution_date", "subject", "jurisdiction",
                "person_custom", "last_update", "last_update_message",
                "inactive_organization", "court_info", "ref_docs",
                "process_organization", "documents", "has_session",
                "has_session_video", "process_id",
                "type_court", "instances", "content_all"
            ]
        )

    def test__process_invalid_detail(self):
        """Test invalid process detail error."""
        tratum_api = self.test__login()

        process_number = "00000000000000000000"
        with self.assertRaises(TratumAPIInvalidDocumentException) as context:
            tratum_api.get_process_detail(
                process_number=process_number)
        self.assertEqual(
            str(context.exception),
            "TratumAPIInvalidDocumentException: invalid process number")

    def test__get_process_document_url(self):
        """Get processed document."""
        tratum_api = self.test__login()

        # Random process to test API
        document_url = (
            "Processos/401/10045683220184013400/PJETRF1/" +
            "nao-concedida-a-antecipacao-de-tutela-07-07-2018-15-43.pdf")
        pdf_url = tratum_api.get_process_document_url(
            document_url=document_url)
        self.assertEqual(
            pdf_url.split('?')[0],
            'https://s3.us-east-2.amazonaws.com/process-files/Processos'
            '/401/10045683220184013400/PJETRF1/'
            'nao-concedida-a-antecipacao-de-tutela-07-07-2018-15-43.pdf'
        )

    def test__download_process_document(self):
        """Get processed document."""
        tratum_api = self.test__login()

        # Random process to test API
        document_url = (
            "Processos/401/10045683220184013400/PJETRF1/" +
            "nao-concedida-a-antecipacao-de-tutela-07-07-2018-15-43.pdf")
        document_content = tratum_api.download_process_document(
            document_url=document_url)
        self.assertTrue(type(document_content) is bytes)

    def test__remove_from_monitoring(self):
        """Test invalid process monitor error."""
        tratum_api = self.test__login()

        process_number = valid_process_number
        operation_result = tratum_api.remove_monitor_process(
            process_number=process_number)
        self.assertEqual(operation_result, True)

import sys

from azure.core.pipeline.policies import RetryPolicy
from django.test import TestCase, override_settings


_connection_str = (
    'DefaultEndpointsProtocol=https;'
    'AccountName=djangoace;'
    'AccountKey=1234'
)
_tenant_id = '1234'
_client_id = '1234'
_client_secret = '1234'
_endpoint = 'https://endpoint'
_key_credential = '1234'


class TestSettings(TestCase):

    def setUp(self) -> None:
        del sys.modules['django_azure_communication_email.settings']
        del sys.modules['django_azure_communication_email']

    @override_settings(AZURE_COMMUNICATION_CONNECTION_STRING=_connection_str)
    def test_connection_string(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.CONNECTION_STRING, _connection_str)

    @override_settings(AZURE_TENANT_ID=_tenant_id)
    def test_tenant_id(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.TENANT_ID, _tenant_id)

    @override_settings(AZURE_CLIENT_ID=_client_id)
    def test_client_id(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.CLIENT_ID, _client_id)

    @override_settings(AZURE_CLIENT_SECRET=_client_secret)
    def test_client_secret(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.CLIENT_SECRET, _client_secret)

    @override_settings(AZURE_COMMUNICATION_ENDPOINT=_endpoint)
    def test_endpoint(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.ENDPOINT, _endpoint)

    @override_settings(AZURE_KEY_CREDENTIAL=_key_credential)
    def test_key_credential(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.KEY_CREDENTIAL, _key_credential)

    @override_settings(AZURE_COMMUNICATION_TRACKING_DISABLED=True)
    def test_tracking_disabled_1(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.TRACKING_DISABLED, True)

    @override_settings(AZURE_COMMUNICATION_TRACKING_DISABLED=False)
    def test_tracking_disabled_2(self):
        from django_azure_communication_email import settings
        self.assertEqual(settings.TRACKING_DISABLED, False)

    def test_retry_policy_no_retries(self):
        retry_policy = RetryPolicy.no_retries()
        with override_settings(AZURE_COMMUNICATION_RETRY_POLICY=retry_policy):
            from django_azure_communication_email import settings
            self.assertEqual(settings.RETRY_POLICY, retry_policy)

    def test_retry_policy_custom(self):
        retry_policy = RetryPolicy(retry_total=5, retry_backoff_factor=0.5)
        with override_settings(AZURE_COMMUNICATION_RETRY_POLICY=retry_policy):
            from django_azure_communication_email import settings
            self.assertEqual(settings.RETRY_POLICY, retry_policy)
            self.assertEqual(settings.RETRY_POLICY.total_retries, 5)
            self.assertEqual(settings.RETRY_POLICY.backoff_factor, 0.5)

    def test_retry_policy_none(self):
        from django_azure_communication_email import settings
        # When not set, should default to None (uses SDK default)
        self.assertIsNone(settings.RETRY_POLICY)

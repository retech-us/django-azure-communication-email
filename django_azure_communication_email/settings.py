from django.conf import settings


CONNECTION_STRING = getattr(
    settings, 'AZURE_COMMUNICATION_CONNECTION_STRING', None,
)
TENANT_ID = getattr(settings, 'AZURE_TENANT_ID', None)
CLIENT_ID = getattr(settings, 'AZURE_CLIENT_ID', None)
CLIENT_SECRET = getattr(settings, 'AZURE_CLIENT_SECRET', None)
ENDPOINT = getattr(settings, 'AZURE_COMMUNICATION_ENDPOINT', None)
KEY_CREDENTIAL = getattr(settings, 'AZURE_KEY_CREDENTIAL', None)

TRACKING_DISABLED = getattr(
    settings, 'AZURE_COMMUNICATION_TRACKING_DISABLED', False,
)

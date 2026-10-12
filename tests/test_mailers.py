import unittest

import django
from django.core.mail import EmailMessage
from django.test import TestCase, override_settings

from django_azure_communication_email import EmailBackend


_connection_str = (
    'DefaultEndpointsProtocol=https;'
    'AccountName=djangoace;'
    'AccountKey=1234'
)
_options_connection_str = (
    'DefaultEndpointsProtocol=https;'
    'AccountName=options;'
    'AccountKey=5678'
)


class EmailClientStub:
    """Behaves like `azure.communication.email.EmailClient`."""

    def __init__(self):
        self.messages = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):  # noqa
        pass

    def begin_send(self, message):
        self.messages.append(message)


def _mailers_settings(options):
    return {
        'MAILERS': {
            'default': {
                'BACKEND': 'django_azure_communication_email.EmailBackend',
                'OPTIONS': options,
            },
        },
    }


@unittest.skipUnless(
    django.VERSION >= (6, 1),
    'MAILERS requires Django 6.1+',
)
class TestMailers(TestCase):
    """Integration tests for Django 6.1 MAILERS configuration."""

    @override_settings(**_mailers_settings({'connection_string': _connection_str}))
    def test_mailers_default_resolves_backend(self):
        from django.core import mail

        backend = mail.mailers.default
        self.assertIsInstance(backend, EmailBackend)
        self.assertEqual(backend._connection_string, _connection_str)

    @override_settings(
        AZURE_COMMUNICATION_CONNECTION_STRING=_connection_str,
        **_mailers_settings({'connection_string': _options_connection_str}),
    )
    def test_options_override_project_settings(self):
        from django.core import mail

        backend = mail.mailers.default
        self.assertEqual(backend._connection_string, _options_connection_str)

    @override_settings(**_mailers_settings({
        'connection_string': _connection_str,
        'tracking_disabled': True,
    }))
    def test_tracking_disabled_via_options(self):
        from django.core import mail

        backend = mail.mailers.default
        message = EmailMessage(
            subject='Subject',
            body='plain text',
            from_email='support@company.com',
            to=['foo@company.com'],
        )

        conv_message = backend.convert_message(message)

        self.assertTrue(conv_message['userEngagementTrackingDisabled'])

    @override_settings(**_mailers_settings({'fail_silently': True}))
    def test_fail_silently_via_options(self):
        from django.core import mail

        backend = mail.mailers.default
        backend.open()
        self.assertIsNone(backend._client)

    @override_settings(**_mailers_settings({
        'connection_string': _connection_str,
        'unknown_option': 'ignored',
    }))
    def test_unknown_options_do_not_crash_init(self):
        from django.core import mail

        backend = mail.mailers.default
        self.assertIsInstance(backend, EmailBackend)
        self.assertEqual(backend._connection_string, _connection_str)

    @override_settings(**_mailers_settings({'connection_string': _connection_str}))
    def test_send_message_via_mailers(self):
        from django.core import mail

        backend = mail.mailers.default
        client = EmailClientStub()
        backend._client = client

        message = EmailMessage(
            subject='Subject',
            body='plain text',
            from_email='Support <support@company.com>',
            to=['Foo <foo@company.com>'],
        )
        backend.send_messages([message])

        self.assertEqual(len(client.messages), 1)
        self.assertEqual(
            client.messages[0]['senderAddress'],
            'support@company.com',
        )

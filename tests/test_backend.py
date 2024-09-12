import base64

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.test import TestCase

from django_azure_communication_email import EmailBackend


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


class TestEmailBackend(TestCase):
    """backend.ACEmailBackend()"""

    def setUp(self) -> None:
        self.backend = EmailBackend()
        self.client = self.backend._client = EmailClientStub()

    def test_fail_silent(self):
        backend = EmailBackend(fail_silently=True)
        backend.open()

    def test_fail_not_silent(self):
        backend = EmailBackend(fail_silently=False)
        with self.assertRaises(Exception):
            backend.open()

    def test_convert_plain_email_message(self):
        message = EmailMessage(
            subject='Subject',
            body='plain text',
            from_email='Support <support@company.com>',
            to=['Foo <foo@company.com>'],
            cc=['Bar <bar@company.com>', 'baz@company.com'],
            bcc=['alice@company.com', 'bob@company.com'],
            reply_to=['Reply <reply@company.com>'],
            headers={'X-Header': 'value'},
        )

        conv_message = self.backend.convert_message(message)

        self.assertEqual(conv_message['content']['subject'], message.subject)
        self.assertEqual(conv_message['content']['plainText'], message.body)
        self.assertFalse('html' in conv_message['content'])
        self.assertEqual(conv_message['senderAddress'], 'support@company.com')
        self.assertEqual(
            conv_message['recipients']['to'],
            [
                {'displayName': 'Foo', 'address': 'foo@company.com'},
            ],
        )
        self.assertEqual(
            conv_message['recipients']['cc'],
            [
                {'displayName': 'Bar', 'address': 'bar@company.com'},
                {'displayName': '', 'address': 'baz@company.com'},
            ],
        )
        self.assertEqual(
            conv_message['recipients']['bcc'],
            [
                {'displayName': '', 'address': 'alice@company.com'},
                {'displayName': '', 'address': 'bob@company.com'},
            ],
        )
        self.assertEqual(
            conv_message['replyTo'],
            [
                {'displayName': 'Reply', 'address': 'reply@company.com'},
            ],
        )
        self.assertEqual(conv_message['headers'], {'X-Header': 'value'})
        self.assertFalse('attachments' in conv_message)

    def test_convert_html_email_message(self):
        message = EmailMultiAlternatives(
            subject='Subject',
            body='plain text',
            from_email='Support <support@company.com>',
            to=['Foo <foo@company.com>'],
        )
        message.attach_alternative('<p>html</p>', 'text/html')

        conv_message = self.backend.convert_message(message)

        self.assertEqual(conv_message['content']['subject'], message.subject)
        self.assertEqual(conv_message['content']['plainText'], message.body)
        self.assertEqual(conv_message['content']['html'], '<p>html</p>')
        self.assertEqual(conv_message['senderAddress'], 'support@company.com')
        self.assertEqual(
            conv_message['recipients']['to'],
            [
                {'displayName': 'Foo', 'address': 'foo@company.com'},
            ],
        )
        self.assertFalse('cc' in conv_message)
        self.assertFalse('bcc' in conv_message)
        self.assertFalse('replyTo' in conv_message)
        self.assertFalse('headers' in conv_message)
        self.assertFalse('attachments' in conv_message)

    def test_convert_email_message_with_attachments(self):
        message = EmailMessage(
            subject='Subject',
            body='plain text',
            from_email='Support <support@company.com>',
            to=['Foo <foo@company.com>'],
        )
        message.attach('file.txt', 'content', 'text/plain')

        conv_message = self.backend.convert_message(message)

        self.assertEqual(conv_message['content']['subject'], message.subject)
        self.assertEqual(conv_message['content']['plainText'], message.body)
        self.assertFalse('html' in conv_message['content'])
        self.assertEqual(conv_message['senderAddress'], 'support@company.com')
        self.assertEqual(
            conv_message['recipients']['to'],
            [
                {'displayName': 'Foo', 'address': 'foo@company.com'},
            ],
        )
        self.assertFalse('cc' in conv_message)
        self.assertFalse('bcc' in conv_message)
        self.assertFalse('replyTo' in conv_message)
        self.assertFalse('headers' in conv_message)
        self.assertEqual(len(conv_message['attachments']), 1)
        self.assertDictEqual(
            conv_message['attachments'][0],
            {
                'name': 'file.txt',
                'contentType': 'text/plain',
                'contentInBase64': base64.b64encode(b'content').decode(),
            },
        )

    def test_send_message(self):
        message = EmailMessage(
            subject='Subject',
            body='plain text',
            from_email='Support <support@company.com>',
            to=['Foo <foo@company.com>'],
        )
        self.backend.send_messages([message])

        self.assertEqual(len(self.client.messages), 1)
        self.assertDictEqual(
            self.client.messages[0],
            {
                'senderAddress': 'support@company.com',
                'recipients': {
                    'to': [
                        {'displayName': 'Foo', 'address': 'foo@company.com'},
                    ],
                },
                'content': {
                    'subject': 'Subject',
                    'plainText': 'plain text',
                },
            },
        )
        self.assertIsNone(self.backend._client)

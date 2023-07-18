import logging
from typing import Any, Dict, Iterable, List, Optional

from azure.communication.email import EmailClient

from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend

from . import attachment, settings, utils


logger = logging.getLogger('django_azure_communication_email')


class ACEmailBackend(BaseEmailBackend):
    """A Django Email backend that uses Azure Communication Email service."""

    def __init__(
        self,
        *,
        connection_string: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        endpoint: Optional[str] = None,
        key_credential: Optional[str] = None,
        fail_silently=False,
        **kwargs,
    ) -> None:
        super().__init__(fail_silently=fail_silently, **kwargs)

        self._connection_string = connection_string \
            or settings.CONNECTION_STRING
        self._tenant_id = tenant_id or settings.TENANT_ID
        self._client_id = client_id or settings.CLIENT_ID
        self._client_secret = client_secret or settings.CLIENT_SECRET
        self._endpoint = endpoint or settings.ENDPOINT
        self._key_credential = key_credential or settings.KEY_CREDENTIAL

        self._client: EmailClient | None = None

    def open(self) -> None:
        if self._client is not None:
            return

        try:
            if conn_str := self._connection_string:
                self._client = EmailClient.from_connection_string(conn_str)
            elif self._tenant_id and self._endpoint:
                from azure.identity import DefaultAzureCredential
                self._client = EmailClient(
                    self._endpoint,
                    DefaultAzureCredential(),  # type: ignore
                )
            elif self._key_credential and self._endpoint:
                from azure.core.credentials import AzureKeyCredential
                self._client = EmailClient(
                    self._endpoint,
                    AzureKeyCredential(self._key_credential),
                )
            else:
                raise ImproperlyConfigured(
                    'You must specify either a connection string,'
                    ' or tenant ID & client ID & client secret & communication'
                    ' endpoint, or key credential & communication endpoint.'
                )
        except Exception as exc:  # noqa
            if not self.fail_silently:
                raise
            logger.warning(
                'Failed to open connection to Azure Communication Email.',
                exc_info=exc,
            )

    def close(self) -> None:
        self._client = None

    def send_messages(self, email_messages: Iterable[EmailMessage]) -> int:
        """
        It's your responsibility to validate all data before sending an email.
        """
        if not email_messages:
            return 0

        self.open()
        if self._client is None:
            # failed silently
            return 0

        sent = 0
        with self._client:
            for message in email_messages:
                try:
                    self._client.begin_send(self.convert_message(message))
                    sent += 1
                except Exception as exc:  # noqa
                    if not self.fail_silently:
                        raise
                    logger.warning('Failed to send email.', exc_info=exc)

        self.close()
        return sent

    def convert_message(self, message: EmailMessage) -> Dict[str, Any]:
        """Converts the EmailMessage object to dictionary."""
        msg = {
            'senderAddress': utils.get_name_and_email(message.from_email)[1],
            'content': {'subject': message.subject},
            'recipients': {},
        }
        if message.body:
            msg['content']['plainText'] = message.body
        if html_msg := utils.get_html_message(message):
            msg['content']['html'] = html_msg
        if message.to:
            msg['recipients']['to'] = self._build_recipients(message.to)
        if message.cc:
            msg['recipients']['cc'] = self._build_recipients(message.cc)
        if message.bcc:
            msg['recipients']['bcc'] = self._build_recipients(message.bcc)
        if message.attachments:
            msg['attachments'] = [
                self._build_attachment(file)
                for file in message.attachments
            ]
        if message.extra_headers:
            msg['headers'] = message.extra_headers
        if message.reply_to:
            msg['replyTo'] = self._build_recipients(message.reply_to)
        if settings.TRACKING_DISABLED:
            msg['userEngagementTrackingDisabled'] = True

        return msg

    @staticmethod
    def _build_recipients(recipients: Iterable[str]) -> List[Dict[str, str]]:
        return [
            {'displayName': name, 'address': email}
            for name, email in map(utils.get_name_and_email, recipients)
        ]

    @staticmethod
    def _build_attachment(file: attachment.Attachment) -> Dict[str, str]:
        converter = attachment.get_converter(file)
        return {
            'name': converter.get_filename(),
            'attachmentType': converter.get_filetype(),
            'contentInBase64': converter.get_content(),
        }

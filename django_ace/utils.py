import re
from typing import Tuple

from django.core.mail import EmailMessage, EmailMultiAlternatives


_RE_SENDER_NAME = re.compile(r'^([^<>]+)\s<([^<>]+)>$')


def get_name_and_email(address) -> Tuple[str, str]:
    """Returns the name and email from addresses like
    "Contact <contact@company.com>".
    """
    if custom_sender_name := _RE_SENDER_NAME.search(address):
        return custom_sender_name.groups()  # type: ignore
    else:
        return '', address


def get_html_message(message: EmailMessage) -> str:
    """Returns None if the email is plain text only, otherwise returns
    the HTML message.
    """
    if isinstance(message, EmailMultiAlternatives):
        for alt_msg, msg_type in message.alternatives:
            if msg_type == 'text/html':
                return alt_msg
    return ''

import base64
import re
from email.charset import Charset
from email.mime.base import MIMEBase
from typing import Tuple, Union


Attachment = Union[MIMEBase, Tuple[str, Union[str, bytes], str]]


class BaseConverter:

    def __init__(self, obj: Attachment):
        self.obj = obj

    def get_filename(self) -> str:
        raise NotImplementedError

    def get_filetype(self) -> str:
        raise NotImplementedError

    def get_content(self) -> str:
        """Returns the base64 encoded string."""
        raise NotImplementedError


class MIMEBaseConverter(BaseConverter):
    """Class for MIME attachments."""

    _RE_MIMETYPE = re.compile(r'^([A-Za-z0-9-./]+)')
    _RE_CHARSET = re.compile(r'charset=.([A-Za-z0-9-./]+).')

    def get_filename(self) -> str:
        return self.obj.get_filename(failobj='untitled')

    def get_filetype(self) -> str:
        return self._RE_MIMETYPE.search(self.obj.get_content_type()).group(1)

    def get_content(self) -> str:
        payload = self.obj.get_payload()

        encoding = str(self.obj.get('content-transfer-encoding', '')).lower()
        if encoding == 'base64':
            return payload

        return base64.b64encode(payload.encode(self.get_charset())).decode()

    def get_charset(self) -> str:
        charset = self.obj.get_charset()

        if isinstance(charset, Charset):
            charset = charset.get_output_charset()

        if not charset:
            found = self._RE_CHARSET.search(self.obj.get_content_type())
            charset = found.group(1) if found else 'ascii'

        return charset


class TupleBaseConverter(BaseConverter):
    """Class for attachments that are a triple of (name, type, content)."""

    def get_filename(self) -> str:
        return self.obj[0]

    def get_filetype(self) -> str:
        return self.obj[2]

    def get_content(self) -> str:
        content = self.obj[1]
        if isinstance(content, str):
            content = content.encode()

        return base64.b64encode(content).decode()


def get_converter(attachment: Attachment) -> BaseConverter:
    if isinstance(attachment, MIMEBase):
        return MIMEBaseConverter(attachment)
    elif isinstance(attachment, tuple):
        return TupleBaseConverter(attachment)
    else:
        raise TypeError(f'Unsupported attachment type: {type(attachment)}')

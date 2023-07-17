import base64
from email.mime.nonmultipart import MIMENonMultipart

from django.test import TestCase

from django_ace import attachment


class TestGetConverter(TestCase):
    """attachment.get_converter()"""

    def test_getting_mime_base_converter(self):
        msg = MIMENonMultipart('application', 'http')
        converter = attachment.get_converter(msg)
        self.assertIsInstance(converter, attachment.MIMEBaseConverter)

    def test_getting_tuple_base_converter(self):
        att_file = ('file.txt', 'file content', 'text/plain')
        converter = attachment.get_converter(att_file)
        self.assertIsInstance(converter, attachment.TupleBaseConverter)

    def test_unknown_attachment_type(self):
        att_file = object()
        with self.assertRaises(TypeError):
            attachment.get_converter(att_file)


class TestTupleBaseConverter(TestCase):
    """attachment.TupleBaseConverter()"""

    def test_plain_text_content(self):
        att_file = ('file.txt', 'file content', 'text/plain')
        converter = attachment.TupleBaseConverter(att_file)

        self.assertEqual(converter.get_filename(), att_file[0])
        self.assertEqual(converter.get_filetype(), att_file[2])
        self.assertEqual(
            converter.get_content(),
            base64.b64encode(att_file[1].encode()).decode(),
        )

    def test_bytes_content(self):
        att_file = ('file.txt', b'file content', 'application/octet-stream')
        converter = attachment.TupleBaseConverter(att_file)

        self.assertEqual(converter.get_filename(), att_file[0])
        self.assertEqual(converter.get_filetype(), att_file[2])
        self.assertEqual(
            converter.get_content(),
            base64.b64encode(att_file[1]).decode(),
        )


class TestMimeBaseConverter(TestCase):
    """attachment.MIMEBaseConverter()"""

    def test_bytes_content(self):
        payload = b'file content'
        filename = 'file.txt'
        filetype = 'application/octet-stream'

        msg = MIMENonMultipart(*filetype.split('/'))
        msg['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.set_payload(payload)

        converter = attachment.MIMEBaseConverter(msg)

        self.assertEqual(converter.get_filename(), filename)
        self.assertEqual(converter.get_filetype(), filetype)
        self.assertEqual(
            converter.get_content(),
            base64.b64encode(payload).decode(),
        )

    def test_bytes_b64encoded_content(self):
        payload = base64.b64encode(b'file content')
        filetype = 'application/octet-stream'

        msg = MIMENonMultipart(*filetype.split('/'))
        msg['Content-Disposition'] = f'attachment;'
        msg['Content-Transfer-Encoding'] = 'base64'
        msg.set_payload(payload)

        converter = attachment.MIMEBaseConverter(msg)

        self.assertEqual(converter.get_filename(), 'untitled')
        self.assertEqual(converter.get_filetype(), filetype)
        self.assertEqual(converter.get_content(), payload.decode())

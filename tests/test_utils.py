from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.test import TestCase

from django_azure_communication_email import utils


class TestGetNameAndEmail(TestCase):
    """utils.get_name_and_email()"""

    def test_email_only_presented(self):
        recipient = 'contact@company.com'
        name, email = utils.get_name_and_email(recipient)
        self.assertEqual(name, '')
        self.assertEqual(email, recipient)

    def test_name_and_email_presented(self):
        recipient = 'Contact <contact@company.com>'
        name, email = utils.get_name_and_email(recipient)
        self.assertEqual(name, 'Contact')
        self.assertEqual(email, 'contact@company.com')


class TestGetHtmlMessage(TestCase):
    """utils.get_html_message()"""

    def test_plain_text_inside_ordinal_email_message(self):
        message = EmailMessage(
            subject='Subject',
            body='Body',
            from_email='contact@company.com',
        )
        self.assertEqual(utils.get_html_message(message), '')

    def test_html_inside_ordinal_email_message(self):
        message = EmailMessage(
            subject='Subject',
            body='<html>Body</html>',
            from_email='contact@company.com',
        )
        self.assertEqual(utils.get_html_message(message), '')

    def test_plain_text_only_inside_email_multi_alternatives(self):
        message = EmailMultiAlternatives(
            subject='Subject',
            body='Body',
            from_email='contact@company.com',
        )
        self.assertEqual(utils.get_html_message(message), '')

    def test_plain_text_and_html_inside_email_multi_alternatives(self):
        message = EmailMultiAlternatives(
            subject='Subject',
            body='Body',
            from_email='contact@company.com',
        )
        html = '<html>Body</html>'
        message.attach_alternative(html, 'text/html')
        self.assertEqual(utils.get_html_message(message), html)

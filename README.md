# Django Azure Communication Email

[![Unit tests](https://github.com/rebotics/django-azure-communication-email/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/rebotics/django-azure-communication-email/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/django-azure-communication-email.svg)](https://badge.fury.io/py/django-azure-communication-email)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://img.shields.io/badge/python-3.8+-blue)
[![Django](https://img.shields.io/badge/django-2.2+-blue.svg)](https://img.shields.io/badge/django-2.2+-blue)

A Django email backend for Azure Communication Email service.


## Installation
Run the following on your system:

    pip install django-azure-communication-email

Then, add these settings to your Django `settings.py`:

    EMAIL_BACKEND = 'django_azure_communication_email.EmailBackend'

    AZURE_COMMUNICATION_CONNECTION_STRING = '...'
    # OR
    AZURE_KEY_CREDENTIAL = '...'
    AZURE_COMMUNICATION_ENDPOINT = '...'

If you prefer to use Azure Active Directory authentication, you can use the
following `settings.py` instead:

    EMAIL_BACKEND = 'django_azure_communication_email.EmailBackend'
    
    AZURE_COMMUNICATION_ENDPOINT = '...'
    
    # Note: make sure to set the following environment variables:
    # AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

Now, when you use `django.core.mail.send_mail`, Azure Communication Email
service will send the messages by default.

## Running Tests
To run the tests::

    python runtests.py

If you want to debug the tests, just add this file as a python script to your IDE run configuration.

## Creating a Release

To create a release:

* Run `poetry version {patch|minor|major}` as explained in [the docs](https://python-poetry.org/docs/cli/#version).
  This will update the version in `pyproject.toml`.
* Commit that change and use git to tag that commit with a version that matches the pattern `v*.*.*`.
* Push the tag and the commit (note some IDEs don't push tags by default).

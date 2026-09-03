# Django Azure Communication Email

[![Unit tests](https://github.com/rebotics/django-azure-communication-email/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/rebotics/django-azure-communication-email/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/django-azure-communication-email.svg)](https://badge.fury.io/py/django-azure-communication-email)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://img.shields.io/badge/python-3.10+-blue)
[![Django](https://img.shields.io/badge/django-3.2+--6.1-blue.svg)](https://img.shields.io/badge/django-3.2+--6.1-blue)

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

## Configuring with MAILERS (Django 6.1+)

Django 6.1 introduced the [`MAILERS`](https://docs.djangoproject.com/en/6.1/ref/settings/#std-setting-MAILERS)
setting as the replacement for `EMAIL_BACKEND`. The legacy `EMAIL_BACKEND`
approach above still works, but projects on Django 6.1+ should migrate to
`MAILERS` before Django 7.0 removes the old settings.

Connection string example:

```python
MAILERS = {
    "default": {
        "BACKEND": "django_azure_communication_email.EmailBackend",
        "OPTIONS": {
            "connection_string": "...",
        },
    },
}
```

Key credential example:

```python
MAILERS = {
    "default": {
        "BACKEND": "django_azure_communication_email.EmailBackend",
        "OPTIONS": {
            "endpoint": "...",
            "key_credential": "...",
        },
    },
}
```

Azure Active Directory example:

```python
MAILERS = {
    "default": {
        "BACKEND": "django_azure_communication_email.EmailBackend",
        "OPTIONS": {
            "endpoint": "...",
            # DefaultAzureCredential reads AZURE_TENANT_ID, AZURE_CLIENT_ID,
            # and AZURE_CLIENT_SECRET from the environment.
        },
    },
}
```

You can define multiple mailers with different configurations (for example,
separate transactional and marketing backends).

### OPTIONS reference

Each key in a mailer's `OPTIONS` dict maps to a constructor argument on
`EmailBackend`. Values in `OPTIONS` take precedence over the equivalent
project-level `AZURE_*` setting.

| OPTIONS key | Equivalent setting |
|---|---|
| `connection_string` | `AZURE_COMMUNICATION_CONNECTION_STRING` |
| `tenant_id` | `AZURE_TENANT_ID` |
| `client_id` | `AZURE_CLIENT_ID` |
| `client_secret` | `AZURE_CLIENT_SECRET` |
| `endpoint` | `AZURE_COMMUNICATION_ENDPOINT` |
| `key_credential` | `AZURE_KEY_CREDENTIAL` |
| `retry_policy` | `AZURE_COMMUNICATION_RETRY_POLICY` |
| `tracking_disabled` | `AZURE_COMMUNICATION_TRACKING_DISABLED` |
| `fail_silently` | (no setting equivalent; controls error handling) |

## Configuring Retry Policy

By default, the Azure SDK will retry failed requests with exponential backoff
(up to 10 total retries). This can cause blocking issues when rate limits are
hit, as workers may wait for extended periods (an hour or more) trying to
send emails.

You can customize the retry behavior by configuring a `RetryPolicy` in your
`settings.py`:

```python
from azure.core.pipeline.policies import RetryPolicy

# Example 1: Disable retries completely (fail immediately)
AZURE_COMMUNICATION_RETRY_POLICY = RetryPolicy.no_retries()

# Example 2: Reduce retries for faster failure (3 retries instead of 10)
AZURE_COMMUNICATION_RETRY_POLICY = RetryPolicy(
    retry_total=3,
    retry_backoff_factor=0.4,  # Shorter backoff time
)

# Example 3: Increase retries for better reliability
AZURE_COMMUNICATION_RETRY_POLICY = RetryPolicy(
    retry_total=15,
    retry_backoff_factor=1.0,  # Longer backoff time
    retry_backoff_max=180,     # Max 3 minutes between retries
)
```

For detailed `RetryPolicy` configuration options, see the
[Azure SDK documentation](https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.pipeline.policies.retrypolicy?view=azure-python).

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

try:
    from functools import singledispatch
except ImportError:
    from singledispatch import singledispatch

import hashlib
import hmac


def compute_webhook_validation_key(app_key):
    """
    Given an application key, compute the SHA256 hex digest (aka "Webhooks
    Validation Key") as directed by:
        https://developers.gadventures.com/docs/webhooks.html#registering-a-webhook

    To successfully respond to incoming webhooks we include this value in
    our response's `X-Application-SHA256` header.
    """
    return hashlib.sha256(app_key.encode('utf-8')).hexdigest()


def compute_request_signature(app_key, request_body):
    """
    Given an application key and request body, compute the signature as
    directed by:
        https://developers.gadventures.com/docs/webhooks.html#verifying-a-webhook

    To verify that incoming webhooks are coming from the G API, we check
    that this value matches the data in the request's `X-Gapi-Signature`
    header.
    """
    request_body = encode_if_not_bytes(request_body)

    return hmac.new(
        app_key.encode('utf-8'),
        request_body,
        hashlib.sha256).hexdigest()


@singledispatch
def encode_if_not_bytes(data):
    data = data.encode('utf-8')
    return data

@encode_if_not_bytes.register(bytes)
def _(data):
    return data

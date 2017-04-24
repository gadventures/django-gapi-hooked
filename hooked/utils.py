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
    return hashlib.sha256(
        encode_if_not_bytes(app_key)).hexdigest()


def compute_request_signature(app_key, request_body):
    """
    Given an application key and request body, compute the signature as
    directed by:
        https://developers.gadventures.com/docs/webhooks.html#verifying-a-webhook

    To verify that incoming webhooks are coming from the G API, we check
    that this value matches the data in the request's `X-Gapi-Signature`
    header.
    """
    return hmac.new(
        encode_if_not_bytes(app_key),
        encode_if_not_bytes(request_body),
        hashlib.sha256).hexdigest()


def encode_if_not_bytes(data):
    # This works in Py2 and 3: `bytes` is just an alias for `str` for Python 2
    # versions since 2.6 (https://docs.python.org/3/whatsnew/2.6.html#pep-3112-byte-literals)
    if isinstance(data, bytes):
        return data

    data = data.encode('utf-8')
    return data

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
    return hmac.new(
        app_key.encode('utf-8'),
        request_body.encode('utf-8'),
        hashlib.sha256).hexdigest()
